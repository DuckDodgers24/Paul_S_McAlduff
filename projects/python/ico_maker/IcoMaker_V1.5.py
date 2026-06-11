import sys
from pathlib import Path

from PIL import Image

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPalette, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget


def resource_path(relative_path):
    """
    Return the absolute path to a resource file, compatible with both
    development and PyInstaller-bundled execution.

    Behavior:
    - When running as a normal Python script, the path is resolved relative
      to the script's directory.
    - When running as a PyInstaller one-file executable, the path is resolved
      relative to the temporary extraction directory (sys._MEIPASS).

    Args:
        relative_path: The filename or relative path to the resource.

    Returns:
        A Path object pointing to the resolved resource location.
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path


class DropArea(QWidget):
    """
    Custom central drop-zone widget for the IcoMaker interface.

    This widget displays the PNG-to-ICO icon row, the drop instruction,
    the 512×512 requirement badge, and the conversion status text. It also
    paints the dark background and dashed rounded drop-zone border.
    """
    def __init__(self, parent=None):
        """
        Build the drop-zone layout, including the file icons, arrow,
        instruction label, and size requirement badge.

        Args:
            parent: Optional parent QWidget for Qt ownership/lifetime management.
        """
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(18)

        icon_row = QHBoxLayout()
        icon_row.setAlignment(Qt.AlignCenter)
        icon_row.setSpacing(2)

        self.png_icon = self.make_icon_label("png-file.png", 80)
        self.ico_icon = self.make_icon_label("ico-file.png", 80)

        arrow_label = QLabel("→")
        arrow_label.setAlignment(Qt.AlignCenter)
        arrow_label.setFont(QFont("Segoe UI", 28))
        arrow_label.setStyleSheet("color: #209bd9;")

        icon_row.addWidget(self.png_icon)
        icon_row.addWidget(arrow_label)
        icon_row.addWidget(self.ico_icon)

        self.drop_label = QLabel(
            '<span style="color:white;">Drop </span>'
            '<span style="color:#209bd9;">PNG</span>'
            '<span style="color:white;"> here</span>'
        )
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setFont(QFont("Segoe UI", 24))

        self.size_label = QLabel("512×512 only")
        self.size_label.setAlignment(Qt.AlignCenter)
        self.size_label.setFont(QFont("Segoe UI", 11))
        self.size_label.setStyleSheet("""
            QLabel {
                color: #209bd9;
                border: 1px solid #209bd9;
                border-radius: 16px;
                padding: 6px 24px;
                background-color: rgba(0, 0, 0, 60);
            }
        """)

        main_layout.addLayout(icon_row)
        main_layout.addWidget(self.drop_label)
        main_layout.addWidget(self.size_label, alignment=Qt.AlignCenter)


    def make_icon_label(self, filename, size):
        """
        Create a centered QLabel containing a scaled icon image.

        Args:
            filename: Name of the image file to load.
            size: Width and height used for the icon label.

        Returns:
            A QLabel containing the scaled icon pixmap.
        """
        label = QLabel()
        label.setFixedSize(size, size)
        label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(str(resource_path(filename)))
        pixmap = pixmap.scaled(
            size,
            size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        label.setPixmap(pixmap)
        return label


    def set_status_text(self, text):
        """
        Update the main drop-area text.

        Args:
            text: New status text to display.
        """
        self.drop_label.setText(text)


    def paintEvent(self, event):
        """
        Paint the dark background and dashed rounded drop-zone border.

        Args:
            event: The Qt paint event provided by the framework.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor("#020A12"))

        drop_rect = self.rect().adjusted(36, 32, -36, -32)

        dashed_pen = QPen(QColor("#1d6f9f"), 1.5)
        dashed_pen.setStyle(Qt.DashLine)
        dashed_pen.setDashPattern([6, 6])

        painter.setBrush(Qt.NoBrush)
        painter.setPen(dashed_pen)
        painter.drawRoundedRect(drop_rect, 18, 18)
        

class IcoMaker(QMainWindow):
    """
    A simple drag-and-drop GUI tool that converts 512×512 PNG files into .ico files.

    Behavior:
    - The main window accepts file drops.
    - Dropped files are filtered to 512×512 PNG images to avoid rescaling
      and preserve icon quality.
    - Valid images are converted to ICO files containing multiple sizes.
    - If an output .ico path already exists, a numbered variant is created:
      e.g., "cat.ico" -> "cat (1).ico" -> "cat (2).ico" ...

    UI:
    - Uses a custom DropArea as the central widget.
    - Displays PNG-to-ICO icons, a drop instruction, a 512×512 requirement badge,
      and conversion status messages.

    Limitations (by design):
    - No recursive folder walking: only the dropped URLs are processed.
    - All image validation is done by opening files with Pillow, not by extension.
    - Invalid images are skipped and reported through the status message.
    - Conversion errors are ignored.
    """
    def __init__(self):
        """
        Create the main window, enable drag-and-drop, and build state/UI.

        Theme-aware icons are applied after the UI is initialized.
        """
        super().__init__()

        # Create window
        self.setWindowTitle("IcoMaker")
        self.setMinimumSize(480, 360)

        # Set window to accept drops
        self.setAcceptDrops(True)

        # Initialize application state and UI
        self.setup_state()
        self.setup_ui()

    # -----------------------------
    # Setup methods
    # -----------------------------

    def setup_state(self):
        """
        Initialize conversion counters and status text.

        State fields:
        - images_dropped: Number of total file paths detected in the last drop.
        - images_converted: Number of valid 512×512 PNG images in the last drop.
        """
        self.images_dropped = 0
        self.images_converted = 0


    def setup_ui(self):
        """
        Build the main UI and set the custom DropArea as the central widget.
        """
        self.drop_area = DropArea()
        self.setCentralWidget(self.drop_area)

        QTimer.singleShot(0, self.apply_theme_icons)

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
        - 256, 128, 64, 48, 32, 24, 20, 16

        Args:
            png_file_paths: List of file path strings that are already validated as 512×512 PNG images.

        Side effects:
        - Writes .ico files to disk next to the source images.
        """
        for path in png_file_paths:
            png_path = Path(path)
            ico_path = png_path.with_suffix(".ico")
            ico_path = self.resolve_ico_name_conflict(ico_path)

            with Image.open(png_path) as img:
                img = img.convert("RGBA")
                img.save(
                    ico_path,
                    format="ICO",
                    sizes = [
                                (256, 256), (128, 128), (64, 64), (48, 48),
                                (32, 32), (24, 24), (20, 20), (16, 16),
                            ]
                )


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
            copy_count += 1


    def update_status_message(self):
        """
        Update the drop-area status text using the current conversion counters.
        """
        if self.images_converted == 0:
            self.drop_area.set_status_text(
                "No valid images found"
            )
        else:
            self.drop_area.set_status_text(
                f"{self.images_converted} of {self.images_dropped} images converted"
            )

    # -----------------------------
    # Drag and drop methods
    # -----------------------------
    
    def dragEnterEvent(self, event):
        """
        Accept a drag-enter event if it contains local file URLs.
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()


    def dragMoveEvent(self, event):
        """
        Accept a drag-move event if it contains local file URLs.
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()


    def dropEvent(self, event):
        """
        Handle a drop by extracting valid images and converting them to ICO.

        Steps:
        - Extract candidate file paths from the drop event.
        - Filter to supported images (PNG, 512×512).
        - Convert all valid images.
        - Update the status message to reflect the result.

        Notes:
        - If nothing valid is found, the event is ignored and no conversion occurs.
        """
        png_file_paths = self.get_images_from_event(event)
        
        if not png_file_paths:
            self.update_status_message()
            event.ignore()
            return

        self.process_image(png_file_paths)
        self.update_status_message()
        event.acceptProposedAction()

  
    def get_images_from_event(self, event):
        """
        Extract local file paths from a Qt drop event and filter to valid images.

        Args:
            event: A QDropEvent containing mime data.

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

    def apply_theme_icons(self):
        """
        Apply a theme-aware window icon based on the current OS palette.

        A light icon is used in dark mode, and a dark icon is used in light mode.
        """
        if self.is_dark_mode():
            window_icon_name = "icomaker-icon-white.ico"

        else:
            window_icon_name = "icomaker-icon-black.ico"

        self.setWindowIcon(QIcon(str(resource_path(window_icon_name))))


    def is_dark_mode(self):
        """
        Determine whether the application is currently using a dark theme.

        This method compares the lightness values of the Window and WindowText
        palette roles from the global QApplication palette.

        Logic:
        - In light mode, WindowText is darker than the Window background.
        - In dark mode, WindowText is lighter than the Window background.

        Returns:
            True if dark mode is detected, otherwise False.

        Notes:
        - This heuristic is more reliable on Windows than checking a fixed
          lightness threshold on the window color alone.
        """
        pal = QApplication.palette()
        window = pal.color(QPalette.Window).lightness()
        text = pal.color(QPalette.WindowText).lightness()
        return text > window
  
    
    def supported_images(self, file_paths):
        """
        Validate a list of dropped file paths and return only supported PNG images.

        Validation rules:
        - The file must open successfully with Pillow.
        - The detected image format must be PNG (img.format == "PNG").
        - The image must be exactly 512×512 pixels.

        Counters:
        - images_dropped is set to len(file_paths) for the most recent drop.
        - images_converted is set to the number of paths that pass validation.

        Args:
            file_paths: List of filesystem paths (strings) extracted from a drop event.

        Returns:
            A list of PNG file path strings that are exactly 512×512.
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
                continue
        self.images_converted = len(png_file_paths)
        return png_file_paths

# -----------------------------
# Application entry point
# -----------------------------

def main():
    """
    Application entry point: create QApplication, show the main window, and run the event loop.

    This function serves as the entry point both when running as a Python script
    and when packaged as a standalone executable (e.g., via PyInstaller).

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
