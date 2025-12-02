import sys
import os

from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QFont,
    QColor,
    QIcon,
    QPalette,
    QAction,
    QMovie,
)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFileDialog,
    QToolBar,
    QSizePolicy,
    QMessageBox,
)

from PySide6.QtCore import (
    Qt,
    QRectF,
    QFile,
    QStandardPaths,
    QBuffer,
    QTimer,
)

from PIL.ImageQt import ImageQt
from PIL import Image

from pillow_heif import register_heif_opener
import pillow_avif

from send2trash import send2trash

"""
Simple image viewer built with PySide6.

Features:
- Opens a single image and scans the containing folder for all supported images.
- Supports static formats: PNG, JPEG, BMP, TIFF, HEIC/HEIF, AVIF, etc.
- Supports animated GIF and WebP via QMovie.
- Zoom in/out with mouse wheel.
- Click-and-drag panning when the zoomed image is larger than the widget.
- Embedded SVG icons (folder, chevrons, trash) stored as base64 strings.
- Delete current file from disk with confirmation.
"""

# enables Pillow to read HEIC/HEIF
register_heif_opener()  

SUPPORTED_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".jpe", ".jfif",
    ".webp", ".gif", ".bmp", ".tif", ".tiff",
    ".heic", ".heif", ".avif", ".avifs"
)


def resource_path(filename):
    """
    Return the absolute path to a resource.
    Works for:
    - Normal Python run
    - PyInstaller onedir (icons in _internal)
    """
    if hasattr(sys, "_MEIPASS"):
        # Running as a bundled exe; resources are in _internal
        base = sys._MEIPASS
    else:
        # Running from the .py file; resources are next to the script
        base = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base, filename)

# --------------------------
# Image loading helpers
# --------------------------

def load_with_pillow(path):
    """
    Load an image using Pillow and convert it to a QPixmap.

    For animated images, only the first frame is used.

    Parameters
    ----------
    path : str
        Filesystem path to the image file.

    Returns
    -------
    QPixmap
        Resulting pixmap. If loading fails, returns an empty QPixmap.
    """
    try:
        img = Image.open(path) 

        # If animated, use first frame
        if getattr(img, "is_animated", False):
            img.seek(0)
            
        qimage = ImageQt(img)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap
    
    except Exception:
        return QPixmap()

def load_pixmap(path):
    """
    Load an image from disk into a QPixmap with multiple fallbacks.

    Order of attempts:
    1. Use QPixmap(path) directly (Qt plugins handle common formats).
    2. Fall back to Pillow for formats like HEIC/AVIF.
    3. If all loading fails, create a placeholder pixmap that displays an error
       message and the filename.

    Parameters
    ----------
    path : str
        Filesystem path to the image file.

    Returns
    -------
    QPixmap
        Loaded or placeholder pixmap.
    """
    # Tries to use Qt
    pixmap = QPixmap(path)
    if not pixmap.isNull():
        return pixmap

    # Falls back on Pillow
    pixmap = load_with_pillow(path)
    if not pixmap.isNull():
        return pixmap

    # Falls back and creats a pixmap placholder
    width  = 800
    height = 600
    filename = os.path.basename(path)

    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#0A1320"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    rect = pixmap.rect()

    # Splits pixmap into two rectangles
    top_rect = QRectF(rect.left(), rect.top(), rect.width(), rect.height() * 0.84)
    bottom_rect = QRectF(rect.left(), rect.height() * 0.20, rect.width(), rect.height() * 0.66)

    # Draws main message
    painter.setPen(Qt.white)
    painter.setFont(QFont("Inter", 26, QFont.Weight.Bold))
    painter.drawText(top_rect, Qt.AlignCenter, "Unable to load image")

    # Draws filename
    painter.setFont(QFont("Inter", 12))

    metrics = painter.fontMetrics()
    max_width = bottom_rect.width() - 40
    display_name = metrics.elidedText(filename, Qt.ElideMiddle, int(max_width))

    painter.drawText(bottom_rect, Qt.AlignCenter, display_name)
   
    painter.end()

    return pixmap

# --------------------------
# Classes
# --------------------------

class ImageWidget(QWidget):
    """
    Central widget responsible for displaying the current image.

    Responsibilities:
    - Store the current pixmap and zoom state.
    - Draw the pixmap scaled and centered in the available space.
    - Support zooming via mouse wheel.
    - Support panning via click-and-drag when the image is larger than the widget.
    - Optionally update frames for an active animation (QMovie).
    """
    def __init__(self, parent=None): # Accepts a parent or none
        """
        Initialize the image display widget.

        Parameters
        ----------
        parent : QWidget or None, optional
            Parent widget, if any.
        """
        super().__init__(parent)
        
        # Zoom state variables
        self._pixmap = None # Accepts QPixmap or None
        self._zoom_factor = 1.0 # Original QPixmap size
        self._min_zoom = 0.05   # 5%
        self._max_zoom = 10.0   # 1000%
        self._user_zoomed = False # Tracks user zooming

        # Pan state variables
        self._pan_active = False
        self._pan_start = None  # QPoint (2D coordinate)
        self._pan_offset_x = 0
        self._pan_offset_y = 0

        # Animation state variables (Qt-only)
        # self._movie = None
        # self._movie_active = False

    def set_animation_frame(self, pixmap):
        """
        Update the currently displayed frame for an active animation.

        This does NOT reset zoom or pan; it simply swaps in the new frame.

        Parameters
        ----------
        pixmap : QPixmap
            The current frame from a QMovie.
        """
        if not pixmap or pixmap.isNull():
            return
        self._pixmap = pixmap
        self.update()

    def clamp_pan_to_bounds(self):
        """
        Keep the pan offset within reasonable bounds.

        If the scaled image is smaller than the widget in a given dimension,
        panning in that dimension is disabled (offset is set to zero).

        When the image is larger than the widget, panning is limited so that
        you cannot drag the image completely off-screen.
        """
        if not self._pixmap or self._pixmap.isNull():
            self._pan_offset_x = 0
            self._pan_offset_y = 0
            return

        widget_width = self.width()
        widget_height = self.height()

        if widget_width <= 0 or widget_height <= 0:
            self._pan_offset_x = 0
            self._pan_offset_y = 0
            return

        scaled_width = self._pixmap.width() * self._zoom_factor
        scaled_height = self._pixmap.height() * self._zoom_factor

        # Horizontal: if the image is narrower than the widget, no horizontal pan.
        if scaled_width <= widget_width:
            self._pan_offset_x = 0
        else:
            half_range_x = (scaled_width - widget_width) / 2.0
            if self._pan_offset_x > half_range_x:
                self._pan_offset_x = half_range_x
            elif self._pan_offset_x < -half_range_x:
                self._pan_offset_x = -half_range_x

        # Vertical: if the image is shorter then the widget, no vertical pan.
        if scaled_height <= widget_height:
            self._pan_offset_y = 0
        else:
            half_range_y = (scaled_height - widget_height) / 2.0
            if self._pan_offset_y > half_range_y:
                self._pan_offset_y = half_range_y
            elif self._pan_offset_y < -half_range_y:
                self._pan_offset_y = -half_range_y

    def set_pixmap(self, pixmap=None): # Accepts QPixmap or None
        """
        Set or replace the current image and reset zoom/pan appropriately.

        - If `pixmap` is None or invalid, clears the view and resets zoom to 1.0.
        - If a valid pixmap is provided and the widget has size, computes an
          initial zoom factor that fits the image into the widget.

        Parameters
        ----------
        pixmap : QPixmap or None, optional
            New image to display, or None to clear.
        """
        self._pixmap = pixmap

        # Resets to no user zooming for new images
        self._user_zoomed = False        

        if not self._pixmap or self._pixmap.isNull():
            self._zoom_factor = 1.0
            self._pan_offset_x = 0
            self._pan_offset_y = 0            
            self.update()
            return

        if self.width() > 0 and self.height() > 0:
            # Computes scaling needed to make the image fit the widget
            scale_x = self.width() / self._pixmap.width()
            scale_y = self.height() / self._pixmap.height()

            # Raw zoom that fits the whole image
            ideal_zoom = min(scale_x, scale_y)

            if ideal_zoom < 1.0:
                # Image is larger than the widget in at least one dimension → shrink it
                self._zoom_factor = max(self._min_zoom, ideal_zoom)
            else:
                # Image is smaller than (or equal to) the widget → show at 100%
                self._zoom_factor = 1.0
        else:
            self._zoom_factor = 1.0

        self._pan_offset_x = 0
        self._pan_offset_y = 0
        self.update()

    def zoom_in(self):
        """Zoom in by a fixed factor (25% increase)."""
        self.set_zoom(self._zoom_factor * 1.25)
        self._user_zoomed = True # Sets to user has zoomed     

    def zoom_out(self):
        """Zoom out by a fixed factor (25% decrease)."""  
        self.set_zoom(self._zoom_factor / 1.25)
        self._user_zoomed = True # Sets to user has zoomed 
        
    def reset_zoom(self):
        """
        Reset zoom to 1.0 (original image size).

        Currently unused in the image viewer, but kept for completeness.
        """
        self.set_zoom(1.0)
        self._user_zoomed = False # Resets to user has not zoomed 
        
    def fit_to_window(self):
        """
        Adjust zoom so the entire image fits inside the widget.

        Currently unused in the viewer: zoom is instead initialized on
        image load based on the widget size.
        """
        if not self._pixmap or self._pixmap.isNull():
            return

        if self.width() == 0 or self.height() == 0:
            return

        scale_x = self.width() / self._pixmap.width()
        scale_y = self.height() / self._pixmap.height()
        self.set_zoom(min(scale_x, scale_y))

    def set_zoom(self, zoom):
        """
        Set the zoom level, clamped between the configured min and max.

        Also clamps the pan offsets so the image doesn't drift off-screen.

        Parameters
        ----------
        zoom : float
            Desired zoom factor (1.0 = original size).
        """
        zoom = max(self._min_zoom, min(self._max_zoom, zoom))
        if abs(zoom - self._zoom_factor) < 0.0001: # ignore tiny zoom changes
            return
        
        self._zoom_factor = zoom

        # Adjust pan so the image doesn't get stuck off-center
        self.clamp_pan_to_bounds()
        
        self.update()

    def paintEvent(self, event):
        """
        Reimplemented QWidget method.

        Handles all drawing: clears the background and draws the current
        pixmap scaled and centered with the current zoom and pan offsets.
        """
        painter = QPainter(self)
        
        # Enables smooth high-quality scaling when zooming   
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # Fills background with Midnight Smoke
        painter.fillRect(self.rect(), QColor("#0A1320"))

        if not self._pixmap or self._pixmap.isNull():
            return

        # Scales size, keeping aspect ratio via a single zoom factor
        scaled_width = self._pixmap.width() * self._zoom_factor
        scaled_height = self._pixmap.height() * self._zoom_factor

        # center the image, then apply pan offsets
        offset_x = (self.width() - scaled_width) / 2.0 + self._pan_offset_x
        offset_y = (self.height() - scaled_height) / 2.0 + self._pan_offset_y

        target_rect = QRectF(
            offset_x,
            offset_y,
            scaled_width,
            scaled_height,
        )
        source_rect = QRectF(
            0.0,
            0.0,
            float(self._pixmap.width()),
            float(self._pixmap.height()),
        )

        painter.drawPixmap(target_rect, self._pixmap, source_rect)

    def resizeEvent(self, event):
        """
        Handle widget resize events.

        If the user has not manually changed zoom for the current image,
        automatically refit the image to the new window size.

        If the user HAS zoomed, keep the current zoom and just clamp pan so the
        image doesn't get stuck off-screen.
        """
        if self._pixmap and not self._pixmap.isNull():
            if not self._user_zoomed:
                # Auto-fit while user hasn't zoomed this image
                self.fit_to_window()
            else:
                # Keep user's zoom, just fix pan bounds
                self.clamp_pan_to_bounds()

        super().resizeEvent(event)

    def wheelEvent(self, event):
        """
        Handle mouse wheel events for zooming.

        Rolling the wheel forward zooms in, rolling backward zooms out.
        """
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()

    def mousePressEvent(self, event):
        """
        Start panning when the left mouse button is pressed over the image.

        Panning is only enabled if the scaled image is larger than the widget
        in at least one dimension.
        """
        if event.button() == Qt.LeftButton and self._pixmap and not self._pixmap.isNull():
            # compute how big the image is *on screen* at the current zoom
            scaled_width = self._pixmap.width() * self._zoom_factor
            scaled_height = self._pixmap.height() * self._zoom_factor

            # if the whole image fits inside the widget, no point panning
            if scaled_width <= self.width() and scaled_height <= self.height():
                return

            # otherwise, enable panning
            self._pan_active = True
            self._pan_start = event.position()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Update pan offsets while the left mouse button is held down.

        The image is dragged according to the mouse movement, within the
        limits enforced by `clamp_pan_to_bounds()`.
        """
        if self._pan_active:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()

            self._pan_offset_x += delta.x()
            self._pan_offset_y += delta.y()

            # Keep pan within valid bounds
            self.clamp_pan_to_bounds()

            self.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        End panning when the left mouse button is released.
        """
        if event.button() == Qt.LeftButton:
            self._pan_active = False
        super().mouseReleaseEvent(event)

class ImageViewerApp(QMainWindow):
    """
    Main application window for the image viewer.

    Responsibilities:
    - Own the ImageWidget used for displaying images.
    - Manage the list of images in the current folder and the current index.
    - Provide a bottom toolbar with Browse / Previous / Next / Delete actions.
    - Handle loading images (static or animated) and wiring them into the widget.
    """ 
    def __init__(self, initial_path=None):
        """
        Initialize the main window and set up state, UI, and signal connections.
        """ 
        super().__init__()

        self.setWindowTitle("Image Viewer")
        self.resize(800, 600) # starting size
        self.setMinimumSize(600, 400) # prevents collapse
        self.setWindowIcon(QIcon(resource_path("ImageViewerApp.ico")))

        # You call your setup methods here
        self.setup_state()
        self.setup_ui()
        self.setup_connections()
        
        # If we were launched with a file path, open it immediately
        if initial_path:
            QTimer.singleShot(0, lambda: self.open_image_from_path(initial_path))
            
    # -----------------------------
    # Class methods
    # -----------------------------

    def setup_state(self):
        """
        Initialize non-UI state for the application.

        Attributes
        ----------
        image_list : list[str]
            List of image paths in the current folder.
        current_index : int
            Index into `image_list` for the currently displayed image.
        current_movie : QMovie or None
            Active QMovie for animated images (GIF/WebP), if any.
        """
        self.image_list = []
        self.current_index = 0
        self.current_movie = None   # Tracks active QMovie
        self.current_movie_buffer = None   # Keeps QBuffer alive for animated images

    def setup_ui(self):
        """
        Build and lay out the UI components for the main window.

        Currently:
        - A central ImageWidget for displaying images.
        - A non-movable bottom QToolBar for navigation and file actions.
        """
        self.image_widget = ImageWidget(self)
        self.setCentralWidget(self.image_widget)
        
        self.bottom_toolbar = QToolBar("Bottom Toolbar", self)
        self.bottom_toolbar.setMovable(False)
        self.bottom_toolbar.setStyleSheet("QToolBar { border: none; }")
        self.addToolBar(Qt.BottomToolBarArea,self.bottom_toolbar)
        
        # create widgets, layouts, menus, etc.
        # Midnight Smoke — #0A1320 @ 60% opacity

    def setup_connections(self):
        """
        Create toolbar actions and connect them to their handlers.
        """
        self.browse_action = QAction("Browse", self)
        self.browse_action.setIcon(QIcon(resource_path("folder.svg")))
        self.browse_action.triggered.connect(self.open_image)
        self.bottom_toolbar.addAction(self.browse_action)

        toolbar_spacer1 = QWidget(self)
        toolbar_spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.bottom_toolbar.addWidget(toolbar_spacer1)

        self.previous_action = QAction("Previous", self)
        self.previous_action.setIcon(QIcon(resource_path("left.svg")))
        self.previous_action.triggered.connect(self.previous_image)
        self.bottom_toolbar.addAction(self.previous_action)

        self.next_action = QAction("Next", self)
        self.next_action.setIcon(QIcon(resource_path("right.svg")))
        self.next_action.triggered.connect(self.next_image)
        self.bottom_toolbar.addAction(self.next_action)

        toolbar_spacer2 = QWidget(self)
        toolbar_spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.bottom_toolbar.addWidget(toolbar_spacer2)        

        self.delete_action = QAction("Delete", self)
        self.delete_action.setIcon(QIcon(resource_path("trash.svg")))
        self.delete_action.triggered.connect(self.delete_image)
        self.bottom_toolbar.addAction(self.delete_action)

    # Additional helper methods

    def get_real_pictures_folder(self):
        """
        Return the best Pictures folder to use.

        Priority:
        1. Qt's PicturesLocation (unless it's OneDrive)
        2. Local ~/Pictures
        3. Home directory
        """

        # Returns Qt's official Pictures folder
        qt_pics = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)

        # Rejects OneDrive-hijacked folders
        if qt_pics and os.path.isdir(qt_pics) and "OneDrive" not in qt_pics:
            return qt_pics

        # Gets local pictures folder in home
        home_dir = os.path.expanduser("~")
        local_pics = os.path.join(home_dir, "Pictures")

        # Returns pictures folder in home directory
        if os.path.isdir(local_pics):
            return local_pics

        # Returns home directory if there is no pictures folder
        return home_dir
    
    def open_image(self):
        """
        Open a file dialog, let the user choose an image, and load its folder.

        Steps:
        - Start in the user's Pictures directory.
        - Let the user pick a single file.
        - Scan the file's folder for all supported image extensions.
        - Sort the image list alphabetically and update current_index.
        - Load the chosen image (with animation support).
        """
        default_dir = self.get_real_pictures_folder()
        
        file_path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select an Image",
            dir=default_dir,
            filter="Images (*.png *.jpg *.jpeg *.jpe *.jfif *.webp *.gif *.bmp *.tif *.tiff *.heic *.heif *.avif *.avifs)"
        )

        if not file_path:
            return

        # Normalize the selected file path
        file_path = os.path.normpath(file_path)

        # Gets folder path
        folder_path = os.path.dirname(file_path)

        # Scans for all images in folder
        all_images = [
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if filename.lower().endswith(SUPPORTED_EXTENSIONS)
        ]

        # Sorts images alphabeticaly
        all_images.sort(key=str.lower)

        # Set image + store list
        self.image_list = all_images
        self.current_index = all_images.index(file_path)

        # Use the unified loader (handles animated vs static)
        self.load_image(file_path)

    def open_image_from_path(self, file_path):
        """
        Open the given image path and load its folder.

        This is used when the program is launched with a file argument,
        e.g., from a file association or drag-and-drop onto the .exe.
        """
        if not file_path:
            return

        # Normalize and verify
        file_path = os.path.normpath(file_path)
        if not os.path.isfile(file_path):
            return

        folder_path = os.path.dirname(file_path)

        # Scan for all supported images in that folder
        all_images = [
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if filename.lower().endswith(SUPPORTED_EXTENSIONS)
        ]
        all_images.sort(key=str.lower)

        self.image_list = all_images

        try:
            self.current_index = all_images.index(file_path)
        except ValueError:
            # If for some weird reason it isn't in the list, bail
            self.current_index = 0
            file_path = all_images[0] if all_images else None

        if file_path:
            self.load_image(file_path)
    
    def previous_image(self):
        """
        Navigate to the previous image in the current folder.

        Wraps around to the last image if currently at the first.
        """
        if not self.image_list:
            return
        
        self.current_index -= 1
        
        if self.current_index < 0:
            self.current_index = (len(self.image_list) -1)

        path = self.image_list[self.current_index]
        self.load_image(path)

    def next_image(self):
        """
        Navigate to the next image in the current folder.

        Wraps around to the first image if currently at the last.
        """
        if not self.image_list:
            return
        
        self.current_index += 1
        
        if self.current_index >= len(self.image_list):
            self.current_index = 0
            
        path = self.image_list[self.current_index]
        self.load_image(path)

    def delete_image(self):
        """
        Delete the currently displayed image from disk and update the viewer.

        Behavior:
        - Ask the user for confirmation.
        - If deletion fails, show a warning.
        - If it succeeds, remove the image from `image_list`.
        - If no images remain, clear the viewer.
        - Otherwise, display the next logical image.
        """
        if not self.image_list:
            return
        
        current_image_path = self.image_list[self.current_index]

        if not os.path.exists(current_image_path):
            return
        
        reply = QMessageBox.question(
            self,
            "Delete File",
            "Are you sure you want to delete this file?    ",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Sends image to trash bin
        try:
            send2trash(current_image_path)
        except:
            QMessageBox.warning(
                self,
                "Delete Failed",
                "Unable to delete this file.    "
            )
            return

        if os.path.exists(current_image_path):
            QMessageBox.warning(
                self,
                "Delete Failed",
                "Unable to delete this file.    "
            )
            return        

        # Removes from the in-memory list
        deleted_index = self.current_index
        del self.image_list[deleted_index]

        # If there are no images left, clear the viewer and bail out
        if not self.image_list:
            self.current_index = -1

            # Stop any active animation so it doesn't keep repainting
            if self.current_movie is not None:
                self.current_movie.stop()
                self.current_movie.deleteLater()
                self.current_movie = None

            if hasattr(self, "current_movie_buffer") and self.current_movie_buffer is not None:
                self.current_movie_buffer.close()
                self.current_movie_buffer = None

            self.image_widget.set_pixmap(None)
            
            # Resets the window title to its default
            self.setWindowTitle("Image Viewer")            
            return

        # Decide which image to show next
        if deleted_index >= len(self.image_list):
            self.current_index = len(self.image_list) - 1
        else:
            self.current_index = deleted_index

        # Load and show the new current image
        new_path = self.image_list[self.current_index]
        self.load_image(new_path)
        
    def load_image(self, path):
        """
        Load an image (static or animated) and display it in the ImageWidget.

        Animated formats (.gif, .webp) are handled with QMovie using an
        in-memory buffer so the original file is not locked. For those:
        - A QMovie is created from a QBuffer stored in `current_movie_buffer`.
        - On the first frame, zoom and pan are reset using `set_pixmap`.
        - Subsequent frames use `set_animation_frame` to preserve zoom/pan.

        All other formats (or animation failure) are handled with `load_pixmap`.
        """
        # Stop previous animation if any
        if self.current_movie is not None:
            self.current_movie.stop()
            self.current_movie.deleteLater()
            self.current_movie = None

        if self.current_movie_buffer is not None:
            # Close and drop the buffer
            self.current_movie_buffer.close()
            self.current_movie_buffer = None
            
        # Displays filename on window title
        self.setWindowTitle(f"Image Viewer – {os.path.basename(path)}")
        file_extension = os.path.splitext(path)[1].lower()

        # Uses Qt animation for GIF / WebP, but only if truly animated
        if file_extension in (".gif", ".webp"):
            # Read the file into memory so QMovie does not lock the file
            qfile = QFile(path)
            if qfile.open(QFile.ReadOnly):
                data = qfile.readAll()
                qfile.close()

                buffer = QBuffer()
                buffer.setData(data)
                if not buffer.open(QBuffer.ReadOnly):
                    buffer = None

                if buffer is not None:
                    movie = QMovie(buffer)

                    # Only treat as animated if it has more than one frame
                    if movie.isValid() and movie.frameCount() > 1:
                        self.current_movie = movie
                        self.current_movie_buffer = buffer
                        first_frame_for_this_movie = True

                        def update_frame(frame_index):
                            nonlocal first_frame_for_this_movie

                            frame_pixmap = movie.currentPixmap()
                            if frame_pixmap.isNull():
                                return

                            if first_frame_for_this_movie:
                                # First frame: reset zoom/pan
                                self.image_widget.set_pixmap(frame_pixmap)
                                first_frame_for_this_movie = False
                            else:
                                # Subsequent frames: preserve zoom/pan
                                self.image_widget.set_animation_frame(frame_pixmap)

                        movie.frameChanged.connect(update_frame)
                        movie.start()
                        return  # do not fall through

                    # If not actually animated, fall through to static loader

        # If QMovie not used or not animated → static loader
        pixmap = load_pixmap(path)
        self.image_widget.set_pixmap(pixmap)
        
# --------------------------
# Application entry point
# --------------------------

def main():
    """
    Application entry point.

    Creates the QApplication, instantiates the main window,
    shows it, and starts the Qt event loop.
    """
    # QApplication MUST be first
    app = QApplication(sys.argv)

    # Force a light Fusion style (ignores system dark mode)
    app.setStyle("Fusion")

    palette = app.palette()
    palette.setColor(QPalette.Window, QColor("#f5f5f5"))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor("#e0e0e0"))
    palette.setColor(QPalette.ButtonText, Qt.black)
    palette.setColor(QPalette.Highlight, QColor("#0078d7"))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)

    initial_path = sys.argv[1] if len(sys.argv) > 1 else None

    # Create window
    window = ImageViewerApp(initial_path=initial_path)
    window.show()

    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# --------------------------
# Do not read this comment 
# --------------------------
