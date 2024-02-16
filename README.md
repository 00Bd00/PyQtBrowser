# PyQtBrowser
### Web Browser with Face Detection and Port Scanning

This Python application combines a web browser with face detection and port scanning capabilities. It's built using several libraries, including PyQt5, OpenCV, socket, and pymongo.

## Key Features:

- Web Browsing:
  - Navigate websites using a built-in web browser.
  - Standard navigation features (back, forward, reload, home)
 
- Face Detection:
  - Detects faces from the webcam.
  - Displays a rectangle around detected faces.
  - Stores timestamps and face coordinates in a MongoDB database.
- Port Scanning:
  - Scans open ports on the current website's host.
  - Displays a list of open ports.

## Dependencies:

- Python 3
- PyQt5
- OpenCV
- socket
- pymongo

## Running the Application:  
1. Install the required dependencies:
```bash
pip install pyqt5 opencv-python socket pymongo
```

2. Run the main script:
```bash
python main.py
```

## Using the Application
- Enter URLs in the address bar and navigate as usual.
- Click the "Scan Face" button to start/stop face detection.
- Click the "Scan" button to scan ports for the current website.

## Important Notes

- The default MongoDB connection string assumes a local MongoDB instance with the specified credentials.
- Port scanning without proper authorization might be illegal or against the target server's terms of service. Use this feature responsibly and ethically.
