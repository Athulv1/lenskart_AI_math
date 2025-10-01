# Lenskart Fixture Placement System

This repository contains an automated layout generation system for **optical retail store floor plans**, built using **FreeCAD** and **OpenCV**.

It reads a store layout image, detects the floorplan boundary, and intelligently places categorized fixtures such as:

- **Wall Fixtures** (e.g. JJ, VC shelves)
- **Floor Fixtures** (Euro Centre, Tables, Benches, Sofas)
- **Clinic and Toilet Units**
- **Back Office Furniture**
- **POS Displays / Screens**

All placements respect spatial constraints, store guidelines, and prevent overlaps.


## 📁 Project Structure

├── main.py # Main driver script to run floorplan analysis and placement

├── FC_Controller.py # FreeCAD-based floorplan builder and fixture placer

├── CV_Controller.py # OpenCV-based image analyzer for detecting edges and corners

├── Fixture.py # Fixture object class that loads geometry and computes sizes

├── fcstd_to_dwg.py # Converts .FCStd to .DWG (via DXF)

├── fcstd_to_dxf.py # DXF export with labels from FreeCAD geometry

├── DESIGN Workflow.pdf # Brand-specific zoning and placement guidelines

├── requirements.txt # Python dependencies

└── assets/ # Contains images and fixture .FCStd models

## 📁 assets link

drive link:- https://drive.google.com/drive/folders/1KRnd-cT164LROfdqFOkEzNui2N9Cce17?usp=drive_link

## ✅ Features

- Automatically detects floorplan from an image

- Computes scale from OCR of measurement markers

- Places fixtures by category in correct zones (e.g. premium, clinic, BOH)

- Applies spacing constraints, mirror placement logic, and screen positioning

- Converts FreeCAD models to DWG/DXF

- Modular architecture for extension

## 🛠 Installation & Setup

### 1. Install FreeCAD

- Download from: [https://www.freecad.org/downloads.php](https://www.freecad.org/downloads.php)

- Tested on **FreeCAD 0.21 or later**

- Ensure path is correct (e.g. `C:\Program Files\FreeCAD 1.0\bin`) and referenced in:

  - `FC_Controller.py`

  - `Fixture.py`

  - `fcstd_to_dwg.py`

### 2. Install ODA File Converter *(for DWG support)*

- Download: [https://www.opendesign.com/guestfiles/oda_file_converter](https://www.opendesign.com/guestfiles/oda_file_converter)

- Update `ODA_CONVERTER_PATH` in `fcstd_to_dwg.py`

### 3. Python Dependencies

pip install -r requirements.txt

4. Install Tesseract OCR (for scale detection)

Download from: https://github.com/tesseract-ocr/tesseract

Add to PATH or set explicitly in rotate_door_wall_windows.py

