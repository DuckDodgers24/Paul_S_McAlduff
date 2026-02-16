![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)

# IcoMaker

A lightweight drag-and-drop ICO converter built with Python and PySide6 (Qt for Python).  
IcoMaker converts high-resolution 512×512 PNG images into multi-resolution Windows `.ico` files with strict validation to ensure maximum icon quality.

---

## Requirements

**Python version:** 3.10 or newer  

**Required packages:**

```bash
pip install PySide6 Pillow
```

---

## Features

- Clean drag-and-drop interface  
- Strict 512×512 PNG validation  
- Guaranteed lossless conversion  
- Automatic multi-resolution ICO generation  
- Automatic filename conflict handling  
- Tooltip-based explanation of format requirements  
- Custom window icon  
- Minimal, distraction-free UI  

---

## Design Philosophy

IcoMaker enforces strict input requirements by design:

- Only **PNG** format is accepted (guaranteed lossless)  
- Only **square images** are accepted (prevents distortion)  
- Only **512×512 resolution** is accepted (ensures clean downscaling)  

These constraints eliminate unpredictable rescaling artifacts and produce consistent, high-quality Windows icons.

---

## Supported Input

- **PNG (exactly 512×512 pixels)**  

Files that do not meet these requirements are silently ignored.

---

## Output

Each valid PNG is converted into a Windows ICO file containing the following embedded sizes:

- 256×256  
- 128×128  
- 64×64  
- 32×32  
- 16×16  

If a target `.ico` file already exists:

```
name.ico
name (1).ico
name (2).ico
```

Automatic numbering prevents overwriting existing files.

---

## Installation

Install required packages:

```bash
pip install PySide6 Pillow
```

Clone or download this repository and place the icon files alongside the script.

---

## Running the Application

From the project directory:

```bash
python IcoMaker.py
```

Then:

1. Drag one or more PNG files onto the window.  
2. Valid files are converted automatically.  
3. Status updates display conversion results.  

---

## Project Structure

```
icomaker/
│
├── IcoMaker.py
├── SoftPawPrint.ico
├── info-circle.png
├── README.md
```

---

## Author

**Paul S. McAlduff**  
GitHub: https://github.com/PaulMcAlduff  
