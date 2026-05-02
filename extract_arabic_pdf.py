import os
import re
import logging
import argparse
from tqdm import tqdm
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
from docx import Document
import pytesseract
from PIL import Image, ImageEnhance
import arabic_reshaper
from bidi.algorithm import get_display as bidi_get_display

# Optional translation support for Python 3.13 compatibility
HAS_TRANSLATOR = False
try:
    from googletrans import Translator
    HAS_TRANSLATOR = True
except ImportError as e:
    logging.getLogger(__name__).debug(f'Translation disabled: {e}')

# Arabic Unicode detection
arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')

def extract_arabic_lines(text):
    lines = text.split('\n')
    arabic_lines = [line.strip() for line in lines if arabic_pattern.search(line)]
    return arabic_lines

def preprocess_image(img):
    """Preprocess image for better OCR"""
    img = img.convert('L')  # Grayscale
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # Increase contrast
    img = img.point(lambda p: 255 if p > 128 else 0)  # Binary threshold
    return img

def extract_pdf_text(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        logging.getLogger(__name__).warning(f"Native extract failed: {e}")
        return ""

def extract_scanned_text(pdf_path, logger):
    try:
        pages = convert_from_path(pdf_path, dpi=300)
        full_text = ""
        for page_num, page in enumerate(tqdm(pages, desc="OCR pages")):
            img = preprocess_image(page)
            page_text = pytesseract.image_to_string(img, lang='ara+eng', config='--psm 6 --oem 3')
            full_text += page_text + '\n'
            logger.debug(f"Page {page_num+1} OCR completed")
        return full_text
    except Exception as e:
        logger.error(f"OCR failed for {pdf_path}: {e}")
        return ""

def main(args):
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=getattr(logging, args.log_level.upper())
    )
    logger = logging.getLogger(__name__)
    
    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)
    
    if not os.path.exists(input_dir):
        logger.error(f"Input directory {input_dir} not found")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return
    
    for file in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            pdf_path = os.path.join(input_dir, file)
            logger.info(f"Processing: {file}")
            
            text = extract_pdf_text(pdf_path)
            is_scanned = len(text.strip()) < 200 or not arabic_pattern.search(text)
            
            if args.force_ocr or is_scanned:
                logger.info("Using OCR mode")
                text = extract_scanned_text(pdf_path, logger)
            
            arabic_lines = extract_arabic_lines(text)
            
            translated = arabic_lines
            if not args.no_translate and HAS_TRANSLATOR and arabic_lines:
                logger.info("Translating Arabic lines...")
                translator = Translator()
                translated = []
                for line in tqdm(arabic_lines, desc="Translating", leave=False):
                    try:
                        trans = translator.translate(line, dest=args.target_lang).text
                        translated.append(trans)
                    except Exception as e:
                        logger.warning(f"Translation failed for line: {e}")
                        translated.append(line)
            else:
                if not HAS_TRANSLATOR:
                    logger.warning("Translation unavailable (Py3.13/googletrans issue). Using Arabic lines. Add --no-translate to suppress.")
                logger.info("Using original Arabic lines (no translation)")
            
            base_name = os.path.splitext(file)[0]
            txt_path = os.path.join(output_dir, f"{base_name}_arabic.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(translated) + '\n')
                logger.info(f"Saved TXT: {txt_path}")
            
            docx_path = os.path.join(output_dir, f"{base_name}_arabic.docx")
            doc = Document()
            for line in translated:
                reshaped = arabic_reshaper.reshape(line)
                bidi_text = bidi_get_display(reshaped)
                doc.add_paragraph(bidi_text)
            doc.save(docx_path)
            logger.info(f"Saved RTL DOCX: {docx_path}")
            
        except Exception as e:
            logger.error(f"Processing {file} failed: {e}")
    
    logger.info("Processing complete.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Advanced Arabic PDF Text Extractor with OCR, RTL, optional translation')
    parser.add_argument('--input_dir', default='pdfs', help='Input PDFs directory (default: pdfs)')
    parser.add_argument('--output_dir', default='output', help='Output directory (default: output)')
    parser.add_argument('--force-ocr', action='store_true', help='Force OCR mode')
    parser.add_argument('--no-translate', action='store_true', help='Skip translation (recommended on Py3.13)')
    parser.add_argument('--target-lang', default='en', help='Translation target language (default: en)')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Log level')
    args = parser.parse_args()
    main(args)
