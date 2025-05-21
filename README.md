# PDF to Image Converter

A Python script to convert PDF files to PNG images with various layout options.

## Description

This tool converts PDF files into PNG images with flexible layout options:
- Single page per image (default)
- Two pages side by side (horizontal layout)
- Two pages stacked vertically (vertical layout)
- Four pages in a 2x2 grid (grid layout)

All images are saved in an organized directory structure inside an `output` folder.

## Requirements

- Python 3
- pdf2image library
- Pillow (PIL) library

## Installation

1. Install the required Python packages:

```bash
pip install pdf2image pillow
```

2. On macOS, you may need to install poppler:

```bash
brew install poppler
```

On Linux:

```bash
apt-get install poppler-utils
```

On Windows, download and install from: http://blog.alivate.com.au/poppler-windows/

## Usage

### Basic Usage

Run the script with the path to your PDF file:

```bash
python main.py /path/to/your/file.pdf
```

### Layout Options

Specify a layout with the `--layout` argument:

```bash
# Two pages side by side
python main.py /path/to/your/file.pdf --layout horizontal

# Two pages stacked vertically
python main.py /path/to/your/file.pdf --layout vertical

# Four pages in a 2x2 grid
python main.py /path/to/your/file.pdf --layout grid
```

You can also specify the number of pages per image with `--pages-per-image`, though this is usually determined by the layout:

```bash
python main.py /path/to/your/file.pdf --layout horizontal --pages-per-image 2
```

Note:
- `single` layout only supports 1 page per image
- `horizontal` and `vertical` layouts support up to 2 pages per image
- `grid` layout requires 4 pages per image (if fewer pages are available for the last grid, blank images will be used to complete the 2x2 grid).

### Output Files

Output images will be stored in `output/filename_layout/pages_X-Y.png` where:
- `filename` is the name of your PDF file without extension
- `layout` is the layout option used
- `X-Y` is the page range included in the image

## Output Structure

```
pdf2imgconverter/
├── main.py
├── output/
│   ├── your_pdf_name_single/
│   │   ├── page_1.png
│   │   ├── page_2.png
│   │   └── ...
│   ├── your_pdf_name_horizontal/
│   │   ├── pages_1-2.png
│   │   ├── pages_3-4.png
│   │   └── ...
│   ├── your_pdf_name_vertical/
│   │   ├── pages_1-2.png
│   │   ├── pages_3-4.png
│   │   └── ...
│   └── your_pdf_name_grid/
│       ├── pages_1-4.png
│       ├── pages_5-8.png
│       └── ...
└── README.md
```