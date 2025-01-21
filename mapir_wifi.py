import subprocess
import time
import requests
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import logging

# Configure logging
LOG_FILE = '/home/nicoladilillo/MAPIRS/mapirs.log'
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=LOG_FILE)

# Constants
MAPIRS_FILE = "/home/nicoladilillo/MAPIRS/MAPIRS.txt"
DEFAULT_PASSWORD = "12345678"
BASE_URL = "http://192.168.1.254"
HTML_FILE = "/home/nicoladilillo/MAPIRS/output.xml"
DCIM_FOLDER = "/DCIM/PHOTO/"
PHOTO_FOLDER = "/home/nicoladilillo/MAPIRS/Photos"
INTERFACE = "wlan1"

# Error codes and messages
ERROR_MESSAGES = {
    -5: "WIFIAPP_RET_FILE_ERROR",
    -11: "WIFIAPP_RET_STORAGE_FULL",
    -12: "WIFIAPP_RET_FOLDER_FULL",
}

# Function Definitions

def run_command(command):
    """
    Executes a shell command and captures the output.
    
    Args:
        command (str): The shell command to execute.
        
    Returns:
        str: The output of the command execution.
    """
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout
    if output != "":
        logging.debug(f"Command executed: {command} - Output: {output}")
    else:
        logging.debug(f"Command executed: {command}")
    return output

def connect_to_wifi(ssid, password):
    """
    Connects to a specified Wi-Fi network.

    Args:
        ssid (str): The SSID of the Wi-Fi network.
        password (str): The password of the Wi-Fi network.
    """
    s
    try:
        logging.info("Disconnecting from any current Wi-Fi connections...")           
        # run_command("sudo nmcli radio wifi off")
        # run_command("sudo nmcli radio wifi on")
        # time.sleep(5)
        
        logging.info(f"Attempting to connect to Wi-Fi network: {ssid}")
        result = run_command(f"sudo nmcli dev wifi connect {ssid} password {password} ifname {INTERFACE}")
        
        logging.info(f"Successfully connected to Wi-Fi!")
        logging.debug(f"Connection details: {result}")
        
        time.sleep(2)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to connect to the Wi-Fi network. Error: {e.stderr}")

def read_networks_from_file(file_path):
    """
    Reads a list of network SSIDs from a file.
    
    Args:
        file_path (str): Path to the file containing SSIDs.
        
    Returns:
        list: A list of SSIDs. If the file is not found, returns an empty list.
    Raises:
        FileNotFoundError: If the file at file_path does not exist.
    """
    # @brief Reads a list of network SSIDs from a file.
    # @param file_path Path to the file containing SSIDs.
    # @return A list of SSIDs.
    
    try:
        with open(file_path, 'r') as file:
            networks = [line.strip() for line in file if line.strip()]
        logging.debug(f"Networks loaded from file: {networks}")
        return networks
    except FileNotFoundError:
        logging.error(f"Error: File {file_path} not found.")
        return []

def response_analysis(url, success_message=""):
    """
    Sends a request to a URL and analyzes the response.
    
    Args:
        url (str): The target URL.
        success_message (str, optional): Message to log upon successful request.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        if "xml" in response.headers.get("Content-Type"):
            root = ET.fromstring(response.text)
            status = int(root.find('Status').text.strip())

            if status in ERROR_MESSAGES:
                logging.error(f"Error Status: {status}, Message: {ERROR_MESSAGES[status]}")
            else:
                logging.info(f"Status: {status} - {success_message}")
        else:
            with open(HTML_FILE, "w") as file:
                file.write(response.text)
            logging.debug(f"List of photos saved to {HTML_FILE}")

    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP Request failed: {e}")
    except ET.ParseError as e:
        logging.error(f"Failed to parse XML: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def execute_camera_photos(camera_reference):
    """
    Executes camera-related photo, setting the camera mode to PHOTO and taking a photo

    Args:
        camera_reference (int): The reference number of the camera based on the Wi-Fi connection (starting from 0).
    """
    logging.debug(f"Starting camera actions for Camera {camera_reference}...")

    # Set the camera to PHOTO mode
    response_analysis(f"{BASE_URL}/?custom=1&cmd=3001&par=0", f"Camera {camera_reference} set to PHOTO mode")

    # Take a photo
    response_analysis(f"{BASE_URL}/?custom=1&cmd=1001", f"Photo taken on Camera {camera_reference}")

def delete_camera_photos(camera_reference):
    """
    Delete all camera-related photos

    Args:
        camera_reference (int): The reference number of the camera based on the Wi-Fi connection (starting from 0).
    """
    logging.debug(f"Starting camera actions for Camera {camera_reference}...")

    # Remove all photos from the camera
    response_analysis(f"{BASE_URL}/?custom=1&cmd=4004", f"Delete all photos from Camera {camera_reference}")

def save_camera_photos(cycle_folder, camera_reference):
    """
    Download camera-related photos, and deleting them after download. Photos are saved in the specified cycle folder.

    Args:
        cycle_folder (str): The folder where photos for the current cycle will be saved.
        camera_reference (int): The reference number of the camera based on the Wi-Fi connection (starting from 0).
    """
    logging.debug(f"Starting downloading photos for Camera {camera_reference}...")

    # Retrieve the list of photos from the camera's storage
    response_analysis(f"{BASE_URL}{DCIM_FOLDER}", f"List of photos retrieved from Camera {camera_reference}")

    # Parse the HTML file to extract photo links
    with open(HTML_FILE, "r") as file:
        soup = BeautifulSoup(file, "html.parser")

    links = soup.find_all("a", href=True)

    # Download photos from the camera
    for link in links:
        file_path = link["href"]
        if DCIM_FOLDER in file_path and not file_path.endswith("del=1"):
            url = f"{BASE_URL}{file_path}"
            filename = file_path.split("/")[-1].replace("?del=1", "")

            logging.debug(f"Downloading {filename} from Camera {camera_reference}...")
            response = requests.get(url)
            if response.status_code == 200:
                with open(f"{cycle_folder}/{filename}", "wb") as file:
                    file.write(response.content)
                logging.info(f"Download completed for {filename} from Camera {camera_reference}")
            else:
                logging.error(f"Failed to download {filename} from Camera {camera_reference}: HTTP {response.status_code}")

    # Delete downloaded photos from the camera
    for link in links:
        file_path = link["href"]
        if DCIM_FOLDER in file_path and file_path.endswith("del=1"):
            url = f"{BASE_URL}{file_path}"
            filename = file_path.split("/")[-1].replace("?del=1", "")

            logging.debug(f"Deleting {filename} from Camera {camera_reference}...")
            response = requests.get(url)
            if response.status_code == 200:
                logging.info(f"Deletion completed for {filename} from Camera {camera_reference}")
            else:
                logging.error(f"Failed to delete {filename} from Camera {camera_reference}: HTTP {response.status_code}")

def reset_wifi_connection(camera_reference):
    """
    Restart WiFi connection camera.

    Args:
        camera_reference (str): The reference identifier for the camera.
    """
    # Set the camera to PHOTO mode
    response_analysis(f"{BASE_URL}/?custom=1&cmd=3018", f"Camera {camera_reference} restart wifi")

if __name__ == "__main__":
    logging.info("Script started.\n")

    # Read the SSID of all the camera
    networks = read_networks_from_file(MAPIRS_FILE)
    n_network = len(networks)
    
    i = 0
    for ssid in networks:
        connect_to_wifi(ssid, DEFAULT_PASSWORD)
        delete_camera_photos(i)
        reset_wifi_connection(i)
        i += 1
                    
    try:
        while True:
            # Create a folder for this cycle using the current timestamp (hourly)
            cycle_start_time = datetime.now().strftime("%Y_%m_%d_%H")
            cycle_folder = os.path.join(PHOTO_FOLDER, cycle_start_time)
            
            flag = True
            # Check if the folder exists, if not create it, otherwise check if it contains 2*n_network files
            if not os.path.exists(cycle_folder):
                os.makedirs(cycle_folder)
                logging.info(f"Created folder for this cycle: {cycle_folder}")
            else:
                if len(os.listdir(cycle_folder)) == 2 * n_network:
                    logging.info(f"Cycle folder {cycle_folder} already exists with the required number of files.")
                    flag = False
                else:
                    # Clear the existing files and recreate it
                    run_command(f"rm -rf {cycle_folder}")
                    os.makedirs(cycle_folder)
                    logging.info(f"Cleared and recreated folder for this cycle: {cycle_folder}")
            
            if flag:
                i = 0
                for ssid in networks:
                    connect_to_wifi(ssid, DEFAULT_PASSWORD)
                    execute_camera_photos(i)
                    reset_wifi_connection(i)
                    i += 1

                i = 0
                for ssid in networks:
                    connect_to_wifi(ssid, DEFAULT_PASSWORD)
                    save_camera_photos(cycle_folder, i)
                    reset_wifi_connection(i)
                    i += 1
                
            now = datetime.now()
            next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
            sleep_time = (next_hour - now).total_seconds()
            logging.info(f"Sleeping for {sleep_time} seconds until the start of the next hour.")
            time.sleep(sleep_time)
    except Exception as e:
        logging.error(e)
