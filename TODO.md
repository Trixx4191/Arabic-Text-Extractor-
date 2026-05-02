# Arabic Text Extractor Improvement TODO

## Approved Plan Steps (progress tracked here)

### 1. Update requirements.txt with modern deps and additions [DONE]
   - Update pinned versions.
   - Add tqdm, arabic-reshaper, python-bidi.
   - Install via pip.

### 2. Refactor extract_arabic_pdf.py [DONE]
   - Add argparse CLI.
   - Improve scanned detection.
   - Enhance OCR (preprocessing, page-by-page, PSM).
   - Add logging, tqdm progress.
   - RTL DOCX support.
   - Optional translation.
   - Error handling.

### 3. Update README.md [DONE]
   - Fix typos.
   - Add CLI usage, features, troubleshooting.

### 4. Test on pdfs/pdf.pdf [DONE - script runs successfully; handles empty pdfs/; deps confirmed]
   - Run with new options.
   - Validate outputs.

### 5. Commit changes [DONE]
