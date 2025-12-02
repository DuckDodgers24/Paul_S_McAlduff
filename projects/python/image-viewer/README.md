![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)

# Image Viewer

A lightweight desktop image viewer built with Python and PySide6 (Qt for Python).  
Image Viewer supports static and animated formats, folder scanning, mouse-wheel zoom, click-and-drag panning, and safe deletion to the system recycle bin.

---

## Requirements

**Python version:** 3.10 or newer

**Required packages:**

```bash
pip install PySide6 Pillow pillow-heif pillow-avif-plugin Send2Trash
```

---

## Features

- Opens a single image and scans the containing folder for all supported images  
- Supports static formats: **PNG, JPEG/JPG/JPE/JFIF, BMP, TIFF/TIF, HEIF/HEIC, AVIF**
- Supports animated **GIF** and **WebP** via Qt’s `QMovie`
  - Uses an in-memory buffer so the file is not locked while playing
  - Only treated as animated if the file contains more than one frame
- **Mouse-wheel zoom**
  - Zoom in/out with the scroll wheel
  - Configurable min/max zoom range (5% to 1000%)
- **Click-and-drag panning**
  - Pan the image when zoomed in and larger than the window
  - Pan is constrained so the image cannot be dragged completely off-screen
- **Automatic fit-to-window**
  - New images are auto-fitted to the window if the user has not zoomed yet
  - Resizing the window refits the image until the user performs a manual zoom
- **Bottom toolbar includes:**
  - Browse (open file dialog)
  - Previous / Next image (with wrap-around)
  - Delete (send current file to system recycle bin)
- **Safe deletion**
  - Confirmation dialog
  - Uses `Send2Trash` for safe deletion
  - Handles edge cases where deletion fails or files are missing
- Built-in placeholder for unreadable/unsupported images
- Custom window icon and SVG toolbar icons
- Sensible default folder selection
  - Prefers system Pictures folder
  - Avoids OneDrive-hijacked locations
  - Falls back to ~/Pictures or the home directory

---

## Supported Formats

### Input

- PNG  
- JPEG / JPG / JPE / JFIF  
- GIF (static & animated)  
- TIFF / TIF  
- WebP (static & animated)  
- BMP  
- HEIF / HEIC (via `pillow-heif`)  
- AVIF / AVIFS (via `pillow-avif-plugin`)  

### Display Behavior

- **Animated GIF / WebP**
  - Played via `QMovie` only if multiple frames exist
  - Zoom and pan are preserved between frames
- **Other formats (including animated HEIF/AVIF)**
  - Loaded as static images
  - Pillow-reported animation uses only the first frame

---

## Installation

Install required packages:

```bash
pip install PySide6 Pillow pillow-heif pillow-avif-plugin Send2Trash
```

Clone or download this repository and place the icons alongside the script.

---

## Running the Application

From the project directory:

```bash
python ImageViewerApp_v2.5.py
```

Run with an initial image:

```bash
python ImageViewerApp_v2.5.py path/to/image.png
```

When launched with a file path (e.g., via file association), the viewer:

1. Opens that image  
2. Scans the containing folder  
3. Builds a sorted list of images  
4. Enables Previous/Next navigation through the folder  

---

## Zooming and Panning

### Zooming
- Scroll **up**: zoom in  
- Scroll **down**: zoom out  

### Auto-fit
- First load: image fits window  
- Resizing: refits unless manually zoomed  
- After manual zoom: user zoom is preserved  

### Panning
- Hold **left mouse button** + drag  
- Only active when image is larger than window  
- Panning is clamped to prevent losing the image  

---

## Deleting Images

Click the **trash icon** to delete the current image.

The program will:

- Ask for confirmation  
- Send the file to the recycle bin via `Send2Trash`  
- Remove it from the image list  
- Advance to next/previous image  
- Clear the viewer if no images remain  

---

## Screenshots

![Image Converter -- Main Window](screenshots/ImageConverterApp_v1.2.png)

---

## Project Structure

Example layout:

```
image_viewer/
│
├── ImageViewerApp_v2.5.py
├── ImageViewerApp.ico
├── folder.svg
├── left.svg
├── right.svg
├── trash.svg
└── README.md
```

If bundling with PyInstaller, icons can be included as data files.  
The included `resource_path` helper ensures proper loading both in normal runs and bundled executables.

---

## Code Overview

### `ImageWidget`
Custom widget responsible for:
- Drawing and scaling the current image  
- Mouse-wheel zoom  
- Drag panning  
- Fit-to-window logic  
- Handling zoom/pan state  
- Displaying animation frames without resetting zoom/pan  

### `ImageViewerApp`

Main window that:
- Owns the `ImageWidget`  
- Manages image lists  
- Handles:
  - Opening images  
  - Sorting directories  
  - Navigation  
  - Deletion  
  - Animated and static image loading via `load_image()`  

### Helper Functions

- `resource_path(filename)` — PyInstaller-safe asset loader  
- `get_real_pictures_folder()` — avoids OneDrive hijacking  
- `load_with_pillow(path)` — Pillow loader → QPixmap  
- `load_pixmap(path)` — Qt → Pillow → placeholder fallback  

---

## Author

**Paul S. McAlduff**  
GitHub: https://github.com/PaulMcAlduff
