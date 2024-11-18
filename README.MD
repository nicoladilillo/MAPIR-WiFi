# WiFi-Controlled MAPIR

## Introduction
The WiFi-controlled MAPIR Camera project is an exciting endeavor that leverages the power of WiFi technology to remotely control a MAPIR camera. This project allows users to wirelessly control the camera, enabling them to capture stunning images and videos from a distance.

## Project Overview
The project involves integrating a WiFi module with the MAPIR camera, enabling it to establish a wireless connection with a controlling device such as a smartphone or computer. This connection allows users to send commands and receive real-time feedback from the camera, providing a seamless and convenient control experience.

## Key Features
- **Wireless Control**: The WiFi module enables users to control the MAPIR camera wirelessly, eliminating the need for physical connections and allowing for greater flexibility in camera placement.
- **Remote Access**: Users can remotely access the camera's functionalities through a dedicated mobile app or a web interface, providing convenience and accessibility from anywhere with an internet connection.
- **Real-time Feedback**: The WiFi connection allows for real-time feedback, enabling users to view the camera's live feed, adjust settings, and capture images or videos with precision.
- **Multi-platform Compatibility**: The project supports multiple platforms, including iOS, Android, and desktop operating systems, ensuring compatibility with a wide range of devices.

## Technical Implementation
The WiFi-controlled MAPIR Camera project involves the following technical components and implementation steps:

### 1. WiFi Module Integration
The MAPIR camera is equipped with a WiFi module that enables wireless communication. The module is connected to the camera's control circuitry, allowing it to send and receive commands.

### 2. Network Configuration
The camera is configured to connect to a local WiFi network, enabling it to establish a connection with the controlling device.

```bash
nmcli device wifi connect "MAPIR-S3WRGN-dbcbdc" password "12345678"
```

### 3. User Interface Development
A user-friendly mobile app or web interface

## Steps

1. Take MAPIR in Photo Mode:

```bash
curl "http://192.168.1.254/?custom=1&cmd=1003"
```

2. Take photo:

```bash
http://192.168.1.254/?custom=1&cmd=1001
```

from the answer save the name of the photo using the following file format.

```
<?xml version="1.0" encoding="UTF-8" ?>
<Function>
<Cmd>1001</Cmd>
<Status>0</Status>
<File>
<NAME>2024_1118_160550_012.JPG</NAME>
<FPATH>A:\DCIM\Photo\2024_1118_160550_012.JPG</FPATH></File>
<FREEPICNUM>34174</FREEPICNUM>
</Function>
```

## Required package

```bash
pip install requests beautifulsoup4
```