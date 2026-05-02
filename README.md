# Arabic Text Extractor

Extract Arabic text from PDFs (native or scanned via OCR), with optional English translation and RTL-formatted DOCX output.

## Features
- Auto-detect scanned vs native PDFs (OCR fallback if text short/no Arabic)
- Advanced OCR: image preprocessing (contrast/threshold), high DPI, page-by-page with progress, Tesseract PSM6/OEM3, lang='ara+eng'
- Full CLI support: customizable dirs, force OCR, skip translation, log levels
- Progress bars for files/pages/translation (tqdm)
- RTL text handling in DOCX (arabic-reshaper + python-bidi)
- Robust error handling & logging
- Dual outputs: plain TXT + formatted DOCX

## Quick Start
1. Setup virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\\Scripts\\activate  # Windows
   ```
2. Install dependencies:
   ```
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

**Linux system dependencies (for pdf2image/pytesseract):**
```
sudo apt update
sudo apt install poppler-utils tesseract-ocr tesseract-ocr-ara
```

3. Place your PDF files in `pdfs/` (or specify --input_dir)
4. Run:
   ```
   python extract_arabic_pdf.py --input_dir pdfs --output_dir output
   ```
   Results in `output/`: `filename_arabic.txt` and `filename_arabic.docx` (RTL).

## CLI Options
```
python extract_arabic_pdf.py --help
```
- `--input_dir DIR` (default: `pdfs`): Input PDFs directory
- `--output_dir DIR` (default: `output`): Output directory
- `--force-ocr`: Force OCR mode (ignore native text)
- `--no-translate`: Skip automatic translation to English
- `--target-lang LANG` (default: `en`): Translation target language
- `--log-level LEVEL` (default: `INFO`): `DEBUG|INFO|WARNING|ERROR`

## Troubleshooting
- **pdf2image errors**: Install `poppler-utils`
- **Tesseract not found**: Install `tesseract-ocr` and `tesseract-ocr-ara`
- **Translation fails**: Google API limits; use `--no-translate` or proxy
- **No output**: Check logs (`--log-level DEBUG`), ensure PDFs contain Arabic (Unicode U+0600+)
- **Slow OCR**: Normal for scanned docs; use higher DPI if needed

## Example
```
python extract_arabic_pdf.py pdfs/my_arabic_book.pdf --force-ocr --no-translate --log-level INFO
```
Processes single PDF or directory.
