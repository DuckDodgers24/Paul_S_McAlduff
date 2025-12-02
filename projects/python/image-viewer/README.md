# Image Viewer

A lightweight desktop image viewer built with Python and PySide6 (Qt for Python).  
Image Viewer supports static and animated formats, folder scanning, mouse-wheel zoom, click-and-drag panning, and safe deletion to the system recycle bin.

---

## Requirements

**Python version:** 3.10 or newer

**Required packages:**

```bash
pip install PySide6 Pillow pillow-heif pillow-avif-plugin Send2Trash
On some systems you may also need platform-specific image plugins or codecs for HEIF/HEIC/AVIF support (handled by pillow-heif and pillow-avif-plugin).

Features
Opens a single image and scans the containing folder for all supported images

Supports static formats: PNG, JPEG/JPG/JPE/JFIF, BMP, TIFF/TIF, HEIF/HEIC, AVIF

Supports animated GIF and WebP via Qt’s QMovie

Uses an in-memory buffer so the file is not locked while playing

Only treats files as animated if they have more than one frame

Mouse-wheel zoom:

Zoom in/out with the scroll wheel

Configurable min/max zoom range (5% to 1000%)

Click-and-drag panning:

Pan the image when zoomed in and larger than the window

Pan is constrained so the image cannot be dragged completely off-screen

Automatic fit-to-window:

New images are auto-fitted to the window if the user has not zoomed yet

Resizing the window refits the image until the user performs a manual zoom

Clean bottom toolbar providing:

Browse (open file dialog)

Previous / Next image in folder (wrap-around navigation)

Delete (send current file to the recycle bin / trash)

Safe deletion:

Confirmation dialog before deleting

Uses Send2Trash to move files to the system trash instead of permanent deletion

Handles edge cases where deletion fails or files are already missing

Built-in placeholder screen for unreadable or unsupported images:

Displays “Unable to load image” and the filename

Custom window icon and SVG toolbar icons (folder, left/right arrows, trash)

Sensible default folder selection:

Prefers the system “Pictures” folder

Avoids OneDrive-hijacked Pictures paths when possible

Falls back to ~/Pictures or the home directory

Supported Formats
Input
PNG

JPEG / JPG / JPE / JFIF

GIF (static and animated)

TIFF / TIF

WebP (static and animated)

BMP

HEIF / HEIC (via pillow-heif)

AVIF / AVIFS (via pillow-avif-plugin)

Display behavior
Animated GIF / WebP:

Played via QMovie if they truly have more than one frame

Zoom and pan are preserved while the animation runs

Other formats (including animated HEIF/AVIF):

Loaded as static images

If Pillow reports an image as animated, only the first frame is shown

Installation
Install the required packages with:

bash
Copy code
pip install PySide6 Pillow pillow-heif pillow-avif-plugin Send2Trash
Clone or download this repository, then place the icons alongside the main script.

Running the Application
From the project directory:

bash
Copy code
python ImageViewerApp_v2.5.py
You can also start the viewer with an initial image:

bash
Copy code
python ImageViewerApp_v2.5.py path\to\some_image.png
When launched with a file path (for example via file association), the viewer:

Opens that image.

Scans the containing folder for all supported image formats.

Builds an alphabetically sorted image list.

Allows navigation through the entire folder with Previous / Next.

Zooming and Panning
Zoom in / out: Use the mouse wheel over the image

Scroll up: zoom in

Scroll down: zoom out

Auto-fit behavior:

When an image is first loaded, it is scaled to fit inside the window while preserving aspect ratio.

Resizing the window refits the image as long as you have not manually zoomed.

Once you zoom manually, the app preserves your zoom level on further resizes.

Panning:

Click and hold the left mouse button and drag when the image is larger than the window.

Panning is constrained so you cannot drag the image fully off-screen.

Deleting Images
Click the trash icon in the bottom toolbar to delete the current image.

The app will:

Ask for confirmation before deletion.

Use Send2Trash so the file goes to the system recycle bin instead of being permanently deleted.

Refresh the in-memory image list and move to the next or previous image.

If no images remain, the viewer clears the image and resets to the default title.

Project Structure
Example layout:

text
Copy code
image_viewer/
│
├── ImageViewerApp_v2.5.py
├── ImageViewerApp.ico
├── folder.svg
├── left.svg
├── right.svg
├── trash.svg
└── README.md
If you bundle the application with PyInstaller, these icon files can be included as data files and are loaded at runtime using a resource_path helper that works both for normal Python runs and bundled executables.

Code Overview
The program is structured around:

ImageWidget

Custom QWidget used as the central widget.

Handles all drawing, scaling, zooming, and panning.

Manages zoom state and pan offsets.

Provides helper methods like:

set_pixmap(pixmap) — set the current image and auto-fit.

set_animation_frame(pixmap) — update frames for active animations while preserving zoom/pan.

fit_to_window() — compute and apply a zoom factor that fits the image.

set_zoom(zoom) / clamp_pan_to_bounds() — control zoom and keep the image on screen.

ImageViewerApp

Main QMainWindow for the application.

Owns the ImageWidget, the toolbar, and the global state:

image_list

current_index

current_movie and current_movie_buffer (for animations)

Handles:

Opening images via QFileDialog

Scanning and sorting images in the selected folder

Previous / Next navigation

Deleting the current image safely

Loading static vs animated images with:

load_image(path)

Helper functions

resource_path(filename) — returns a usable path for icons in both normal runs and PyInstaller bundles.

get_real_pictures_folder() — finds the best default folder, avoiding OneDrive where possible.

load_with_pillow(path) — loads images via Pillow and converts them to QPixmap.

load_pixmap(path) — tries Qt’s native loaders first, then falls back to Pillow, and finally to a placeholder if all else fails.

Author
Paul S. McAlduff
GitHub: https://github.com/PaulMcAlduff

Copy code

