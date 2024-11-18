import requests
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET

# Define the file path and base URL
html_file = "output.xml"
base_url = "http://192.168.1.254"
DCIM_FOLDER = "/DCIM/PHOTO/"
PHOTO_FODLER = "Photos"

# Error codes and messages
error_messages = {
    -5: "WIFIAPP_RET_FILE_ERROR",
    -11: "WIFIAPP_RET_STORAGE_FULL",
    -12: "WIFIAPP_RET_FOLDER_FULL",
}

def response_analysis(url, success_message=""):
    # Fetch the XML from the URL
    try:
        response = requests.get(url)
        
        # Raise an error for bad HTTP responses (4xx or 5xx)
        response.raise_for_status()  

        # Check if the response is XML
        if "xml" in response.headers.get("Content-Type"):
            # Parse the XML from the response content
            root = ET.fromstring(response.text)
            
            # Extract the Status value
            status = int(root.find('Status').text.strip())
        
            # Check for errors and print the corresponding message
            if status in error_messages:
                print(f"Error Status: {status}, Message: {error_messages[status]}")
            else:
                print(f"Status: {status} - {success_message}")
        else:
            # If the response is not XML, save the list of photos to an HTML file
            with open(html_file, "w") as file:
                    file.write(response.text)
            print(f"List of photos saved to {html_file}")

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
############################################################################################################

# Calculate time

from datetime import datetime

# Get the current time
start = datetime.now()

############################################################################################################

# Check if PHOTO_FODLER exists
if not os.path.exists(PHOTO_FODLER):
    os.makedirs(PHOTO_FODLER)

############################################################################################################

# Put in PHOTO mode
url = f"{base_url}/?custom=1&cmd=1003"
response_analysis(url, "Camera set to PHOTO mode")
    
############################################################################################################
    
# Take the PHOTO
url = f"{base_url}/?custom=1&cmd=1001"
response_analysis(url, "Photo taken")

############################################################################################################

# Save list of photos
url = f"{base_url}{DCIM_FOLDER}"
response_analysis(url, "List of photos saved")

#############################################################################################################

# Parse the HTML file to extract the URLs to download
with open(html_file, "r") as file:
    soup = BeautifulSoup(file, "html.parser")

# Find all <a> tags in the table
links = soup.find_all("a", href=True)

#############################################################################################################

# Save photos

# Extract file URLs and download them
for link in links:
    file_path = link["href"]
    # Filter for relevant files
    if DCIM_FOLDER in file_path and not file_path.endswith("del=1"): 
        # Construct the full URL
        url = f"{base_url}{file_path}"
        filename = file_path.split("/")[-1]  # Extract the file name

        # Download the file
        print(f"Downloading {filename} ... ",end="")
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"{PHOTO_FODLER}/{filename}", "wb") as file:
                file.write(response.content)
            print(f"Done")
        else:
            print(f"Failed to download {filename}: HTTP {response.status_code}")

#############################################################################################################

# Delete saved photos
        
for link in links:
    file_path = link["href"]
    # Filter for relevant files
    if DCIM_FOLDER in file_path and file_path.endswith("del=1"): 
        # Construct the full URL
        url = f"{base_url}{file_path}"
        # Extract the file name
        filename = file_path.split("/")[-1][:-6] 

        # Download the file
        print(f"Delete {filename} ... ",end="")
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Done")
        else:
            print(f"Failed to delete {filename}: HTTP {response.status_code}")

print("All downloads completed.")

#############################################################################################################

# Calculate time
end = datetime.now()
print(f"Time taken: {end - start}")