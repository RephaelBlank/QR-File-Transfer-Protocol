# QR File Transfer Protocol

A Python application for transferring files between computers using QR codes as a visual communication channel.

## Prerequisites

- Python 3.10-3.12 (Python 3.13 not supported)
- Visual Studio with:
  - C++ Build Tools
  - MSVC v142 - VS 2019 C++ x64/x86 build tools
  - Windows 10 SDK

## Installation

Install the required Python packages:
```bash
pip install qreader
pip install opencv-python
pip install qrcode
pip install pillow
pip install tk
```

## Usage

### Sending Computer
1. Run `server.py`
2. Select the file to send when the file selection dialog appears
3. The program will open your camera and display QR codes on screen

### Receiving Computer
1. Run `client.py`
2. The program will open your camera and display QR codes
3. When the file transfer is complete, select where to save the received file
4. The saved file will maintain the original filename

## File Structure
- `server.py`: Sender side implementation
- `client.py`: Receiver side implementation
- `VisualTransmissionProtocol.py`: Protocol implementation
- `QrAndCameraProtocol.py`: QR and camera handling

