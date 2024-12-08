# 1st try 
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from docx import Document
import cv2
import numpy as np


# Helper Function: Preprocess Image
def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return binary


# OCR for Images
def ocr_from_image(image_path):
    image = preprocess_image(image_path)
    text = pytesseract.image_to_string(image)
    return text


# OCR for PDFs
def ocr_from_pdf(pdf_path):
    
    images = convert_from_path(pdf_path)
    all_text = []
    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image)
        all_text.append(text)
    return "\n".join(all_text)


# OCR for DOCX
def ocr_from_docx(docx_path):
    doc = Document(docx_path)
    all_text = [p.text for p in doc.paragraphs]
    return "\n".join(all_text)


# Unified OCR Function
def ocr_from_file(file_path):
    extension = os.path.splitext(file_path)[-1].lower()
    if extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        return ocr_from_image(file_path)
    elif extension == '.pdf':
        return ocr_from_pdf(file_path)
    elif extension == '.docx':
        return ocr_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format!")


# Main Execution
if __name__ == "__main__":
    file_path = input("Enter the file path: ").strip()

    if not os.path.exists(file_path):
        print("File does not exist. Please check the path.")
    else:
        try:
            result = ocr_from_file(file_path)
            print("Extracted Text:\n")
            print(result)

            # Save output to a text file
            output_file = "ocr_output.txt"
            with open(output_file, "w") as f:
                f.write(result)
            print(f"\nText saved to {output_file}")

        except Exception as e:
            print(f"An error occurred: {e}")
