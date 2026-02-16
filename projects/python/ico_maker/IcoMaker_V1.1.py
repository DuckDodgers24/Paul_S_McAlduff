import sys
from pathlib import Path

from PIL import Image

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QToolButton


class DropLabel(QLabel):
    """
    A centered QLabel used as the main "drop zone" UI element.

    This label displays status text (instructions + conversion counts) and draws
    decorative rounded corner brackets over itself using QPainter.

    Notes:
    - The bracket geometry is controlled by 'margin' (inset from edges) and 'arm'
      (length of each bracket segment).
    - The label itself does not handle drag/drop; the main window handles that.
    """
    def __init__(self, parent=None):
        """
        Initialize the label with centered alignment and a bold Calibri font.

        Args:
            parent: Optional parent QWidget for Qt ownership/lifetime management.
        """
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)

        font = QFont("Calibri", 16, QFont.Bold)
        self.setFont(font)
        self.setStyleSheet("color: #555555;")


    def paintEvent(self, event):
        """
        Paint the label normally and then draw rounded corner "brackets" on top.

        The normal QLabel painting (background + text) is handled first by the
        base class. After that, this method overlays 8 short lines (two per
        corner) to create the bracket look.

        Args:
            event: The Qt paint event provided by the framework.
        """
        # Draw the normal label first (background + text)
        super().paintEvent(event)

        # Now draw the corner brackets on top
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        pen = QPen()
        pen.setColor(QColor(51, 51, 51))  
        pen.setWidth(10)                 # thickness of bracket
        pen.setCapStyle(Qt.RoundCap)     # rounded ends like your screenshot
        painter.setPen(pen)

        margin = 22                      # distance from edge
        arm = 46                         # length of each bracket arm

        r = self.rect().adjusted(margin, margin, -margin, -margin)

        # Top-left
        painter.drawLine(r.left(), r.top(), r.left() + arm, r.top())
        painter.drawLine(r.left(), r.top(), r.left(), r.top() + arm)

        # Top-right
        painter.drawLine(r.right() - arm, r.top(), r.right(), r.top())
        painter.drawLine(r.right(), r.top(), r.right(), r.top() + arm)

        # Bottom-left
        painter.drawLine(r.left(), r.bottom(), r.left() + arm, r.bottom())
        painter.drawLine(r.left(), r.bottom() - arm, r.left(), r.bottom())

        # Bottom-right
        painter.drawLine(r.right() - arm, r.bottom(), r.right(), r.bottom())
        painter.drawLine(r.right(), r.bottom() - arm, r.right(), r.bottom())


class IcoMaker(QMainWindow):
    """
    A simple drag-and-drop GUI tool that converts 512x512 PNG files into .ico files.

    Behavior:
    - The main window accepts file drops.
    - Dropped files are filtered to only PNG images that are exactly 512x512
      to avoid rescaling and preserve maximum icon quality.
    - Valid images are converted to ICO files containing multiple sizes.
    - If an output .ico path already exists, a numbered variant is created:
      e.g., "cat.ico" -> "cat (1).ico" -> "cat (2).ico" ...

    UI:
    - Uses a DropLabel as the central widget to show instructions and counts.
    - Displays "X of Y converted" after each drop.

    Limitations (by design):
    - No recursive folder walking: only the dropped URLs are processed.
    - All image validation is done by opening files with Pillow, not by extension.
    - Errors during validation/conversion are ignored (quiet failure).
    """
    def __init__(self):
        """
        Create the main window, set the icon, enable drag-and-drop, and build state/UI.

        The window icon is loaded from 'SoftPawPrint.ico' located alongside the script.
        """
        super().__init__()

        # Create window
        self.setWindowTitle("IcoMaker")
        self.resize(350, 350)
        icon_path = Path(__file__).resolve().parent / "SoftPawPrint.ico"
        self.setWindowIcon(QIcon(str(icon_path)))

        # Set window to accept drops
        self.setAcceptDrops(True)

        # You call your setup methods here
        self.setup_state()
        self.setup_ui()

    # -----------------------------
    # Setup methods
    # -----------------------------

    def setup_state(self):
        """
        Initialize conversion counters and the initial status text.

        State fields:
        - status_message: Text shown in the DropLabel.
        - images_dropped: Number of total file paths detected in the last drop.
        - images_converted: Number of valid 512x512 PNG images in the last drop.
        """
        self.status_message = "PNG to ICO conversion\nDrag & drop image files here\n\n512×512 only"
        self.images_dropped = 0
        self.images_converted = 0


    def setup_ui(self):
        """
        Build the main UI: a DropLabel in the center of the window.

        The label text is set to the current `status_message`.
        """
        self.label = DropLabel()
        self.label.setText(self.status_message)
        self.setCentralWidget(self.label)

        # Info icon (tooltip only), attached to the 512x512 line
        self.info_button = QToolButton(self.label)
        self.info_button.setAutoRaise(True)
        self.info_button.setCursor(Qt.PointingHandCursor)
        self.info_button.setToolTip(
            "Requires 512×512 PNG images to ensure lossless conversion and maximum icon quality."
        )

        info_icon_path = Path(__file__).resolve().parent / "info-circle.png"
        self.info_button.setIcon(QIcon(str(info_icon_path)))
        self.info_button.setIconSize(QSize(16, 16))
        self.info_button.setFixedSize(18, 18)
        self.info_button.show()


    def resizeEvent(self, event):
        """
        Reposition the info icon whenever the window is resized.

        The icon is positioned relative to the geometric center of the DropLabel.
        Offsets are applied to align the icon visually with the "512×512 only" line.

        Offset behavior:
        - Increase x_offset → moves the icon further right
        - Decrease x_offset → moves it left
        - Increase y_offset → moves it down
        - Decrease y_offset → moves it up

        Notes:
        - The offsets are tuned for the current font size and line spacing.
        - If the layout text or spacing changes, the offsets may require adjustment.
        - This method relies on geometric positioning rather than text layout anchors.
        """
        super().resizeEvent(event)

        # Position the icon near the end of the "512x512 only" line.
        # These offsets assume your current font size and line spacing.
        center_x = self.label.width() // 2
        center_y = self.label.height() // 2

        x_offset = 60
        y_offset = 32
        
        self.info_button.move(center_x + x_offset, center_y + y_offset)


    # -----------------------------
    # Main methods
    # -----------------------------
    
    def process_image(self, png_file_paths):
        """
        Convert each validated PNG path into an .ico file with multiple embedded sizes.

        For each input PNG:
        - Determine the output path by replacing the extension with .ico.
        - If the .ico already exists, pick a new name using resolve_ico_name_conflict().
        - Open the PNG with Pillow, convert to RGBA, and save as ICO.

        Output ICO sizes:
        - 256, 128, 64, 32, 16

        Args:
            png_file_paths: List of file path strings that are already validated
                            as 512x512 PNG images.

        Side effects:
        - Writes .ico files to disk next to the source images.
        - Updates the status label after processing.
        """
        for path in png_file_paths:
            png_path = Path(path)
            ico_path = png_path.with_suffix(".ico")
            ico_path = self.resolve_ico_name_conflict(ico_path)

            with Image.open(png_path) as img:
                img = img.convert("RGBA")
                img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        self.update_status_message()


    def resolve_ico_name_conflict(self, ico_path):
        """
        Return a non-conflicting .ico output path.

        If the requested output path does not exist, it is returned unchanged.
        If it already exists, this method finds the first available numbered name:
        - "name.ico" -> "name (1).ico" -> "name (2).ico" -> ...

        Args:
            ico_path: A Path object for the desired output ICO filename.

        Returns:
            A Path that does not already exist on disk.
        """
        if not ico_path.exists():
            return ico_path

        parent = ico_path.parent
        stem = ico_path.stem
        suffix = ico_path.suffix

        copy_count = 1
        while True:
            candidate = parent / f"{stem} ({copy_count}){suffix}"
            if not candidate.exists():
                return candidate
            copy_count = copy_count + 1


    def update_status_message(self):
        """
        Update the on-screen status message using the current counters.

        The message is formatted as:
            "{converted} of {dropped} images converted"

        Then it resets the instructional text beneath it and updates the label.
        """
        self.status_message = f"{self.images_converted} of {self.images_dropped} images converted\nDrag & drop more image files\n\n512x512 only"
        self.label.setText(self.status_message)

    # -----------------------------
    # Drag and drop methods
    # -----------------------------
    
    def dragEnterEvent(self, event):
        """
        Accept or reject a drag-enter event based on whether it contains valid images.

        A drag is accepted if get_images_from_event() returns at least one valid path.
        """ 
        if self.get_images_from_event(event):
            event.acceptProposedAction()
        else:
            event.ignore()


    def dragMoveEvent(self, event):
        """
        Accept or reject a drag-move event based on whether it contains valid images.

        This is called repeatedly as the mouse moves during a drag over the window.
        """
        if self.get_images_from_event(event):
            event.acceptProposedAction()
        else:
            event.ignore()


    def dropEvent(self, event):
        """
        Handle a drop by extracting valid images and converting them to ICO.

        Steps:
        - Extract candidate file paths from the drop event.
        - Filter to supported images (PNG, 512x512).
        - Convert all valid images.
        - Accept the drop action if anything was processed.

        Notes:
        - If nothing valid is found, the event is ignored and no conversion occurs.
        """
        png_file_paths = self.get_images_from_event(event)
        if not png_file_paths:
            event.ignore()
            return

        self.process_image(png_file_paths)

        event.acceptProposedAction()

  
    def get_images_from_event(self, event):
        """
        Extract local file paths from a Qt drop/drag event and filter to valid images.

        Args:
            event: A QDragEnterEvent/QDragMoveEvent/QDropEvent containing mime data.

        Returns:
            A list of file path strings that pass supported_images().
            Returns an empty list if the event contains no URLs.
        """
        mime_data = event.mimeData() # Get the dropped item (files, text, etc.)
        if not mime_data.hasUrls():  # If nothing is dropped, ignore  event and move on
            return []

        file_paths = [url.toLocalFile() for url in mime_data.urls()]
        return self.supported_images(file_paths)

    # -----------------------------
    # Helper methods
    # -----------------------------
    
    def supported_images(self, file_paths):
        """
        Validate a list of dropped file paths and return only supported PNG images.

        Validation rules:
        - The file must open successfully with Pillow.
        - The detected image format must be PNG (img.format == "PNG").
        - The image must be exactly 512x512 pixels.

        Counters:
        - images_dropped is set to len(file_paths) for the most recent drop.
        - images_converted is set to the number of paths that pass validation.

        Args:
            file_paths: List of filesystem paths (strings) extracted from a drop event.

        Returns:
            A list of PNG file path strings that are exactly 512x512.
        """
        self.images_dropped = len(file_paths)
        png_file_paths = []
        for file_path in file_paths:
            if not file_path:
                continue
            try:
                with Image.open(file_path) as img:
                    image_format = img.format
                    if image_format == "PNG":
                        if img.width == img.height == 512:
                            png_file_paths.append(file_path)
            except Exception:
                pass
        self.images_converted = len(png_file_paths)
        return png_file_paths

# -----------------------------
# Application entry point
# -----------------------------

def main():
    """
    Application entry point: create QApplication, show the main window, and run the event loop.

    Notes:
    - QApplication must be created before any QWidget/QMainWindow is instantiated.
    - sys.exit(app.exec()) ensures the process returns the Qt event-loop exit code.
    """
    # QApplication must be first
    app = QApplication(sys.argv)

    # Create window
    window = IcoMaker()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()



# Here there be cats.
