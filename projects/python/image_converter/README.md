![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)

# Image Converter

A desktop GUI application for converting image files between multiple
formats using Python, Tkinter, and Pillow. Image Converter supports
drag-and-drop, batch processing, transparency handling, animation
detection, and safe-conversion dialogs.

## Requirements

Python version: **3.10 or newer**

Required packages:

``` bash
pip install pillow pillow-heif pillow-avif-plugin tkinterdnd2
```

## Features

-   Convert between major image formats:
    -   PNG → JPG / WebP / GIF / TIFF
    -   JPEG → PNG / WebP / GIF / TIFF
    -   GIF (static or animated) → PNG / JPG / WebP / TIFF
    -   WebP (static or animated) → PNG / JPG / GIF / TIFF
    -   Supports BMP, HEIF, HEIC, and AVIF as input formats
-   Drag and drop support for fast file loading
-   Batch conversion for multiple images
-   Automatic detection of image properties:
    -   Transparency
    -   Animation
-   Smart conversion warnings when:
    -   Converting animated images to static formats
    -   Converting transparent images to JPG/TIFF
    -   Converting WebP to GIF (reduced quality)
-   Safe output handling:
    -   Invalid/unreadable file detection
    -   Prevention of excessively long filenames
    -   Automatic opening of output folder after conversion
-   Clean and simple Tkinter GUI

## Supported Formats

### Input

PNG, JPEG/JPG/JPE, GIF, TIFF/TIF, WebP, BMP, HEIF, HEIC, AVIF

### Output

PNG, JPEG, WebP, GIF, TIFF

## Installation

``` bash
pip install pillow pillow-heif pillow-avif-plugin tkinterdnd2
```

## Running the Application

``` bash
python ImageConverterApp_v1.2.py
```

## Handling Transparency and Animation

-   Transparency converted to JPG/TIFF is filled with a white
    background.
-   Animation (GIF/WebP) converted to a static format will keep only the
    first frame.
-   Animated WebP to GIF may lose quality due to GIF limitations.

## Screenshots

![Image Converter -- Main Window](ImageConverterApp_v1.2.png)

## Project Structure

    image_converter/
    │
    ├── ImageConverterApp_v1.2.py
    └── README.md

## Code Overview

The program is structured around a single main class:
**ImageConverterApp**

## Author

**Paul S. McAlduff**\
GitHub: https://github.com/PaulMcAlduff

