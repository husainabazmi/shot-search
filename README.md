
# Shot Search 🔎

A Python-based screenshot search tool that uses OCR (Optical Character Recognition) to extract text from images and lets users search through their screenshots.

## Features

- Extract text from screenshots using Tesseract OCR.
- Supports English and Hindi OCR.
- Store extracted text in an SQLite database.
- Perform fast full-text searches using SQLite FTS5.
- Search using normal, prefix, and exact phrase matching.
- Command-line interface for indexing and searching.
- Streamlit-based web interface for visual screenshot search.
- Automated tests using pytest.

## Tech Stack

- Python
- SQLite and FTS5
- Tesseract OCR
- Pytesseract
- Pillow
- Streamlit
- Pytest

## Project Structure

```text
shot-search/
├── app.py
├── db.py
├── indexer.py
├── main.py
├── ocr.py
├── search.py
├── tests/
├── images/          # Local screenshots (not committed)
├── .gitignore
└── README.md
```

## Requirements

- Python
- Tesseract OCR
- English and Hindi Tesseract language data (for multilingual OCR)

## Installation

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd shot-search
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

Index screenshots:

```bash
python main.py index images
```

Index with English and Hindi OCR:

```bash
python main.py index images --lang eng+hin --force
```

Search from the command line:

```bash
python main.py search "keyword"
```

Launch the web interface:

```bash
python -m streamlit run app.py
```

## Running Tests

```bash
python -m pytest -v
```

## Note

Personal screenshots and local database files are excluded from version control.
