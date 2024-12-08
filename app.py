import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import fitz  
#import PyMuPDF
from docx import Document
import cv2
import numpy as np
import streamlit as st
import requests
from io import BytesIO
from easyocr import Reader
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader


# Helper Function: Preprocess Image
def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Enhanced preprocessing for handwritten text
    adaptive_thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return adaptive_thresh


# OCR for Images using EasyOCR for handwritten improvements
def ocr_from_image(image_path):
    reader = Reader(['en'])  # Supports English; add other languages as needed
    text = reader.readtext(image_path, detail=0)  # Extracts only text
    return "\n".join(text)


# OCR for PDFs
def ocr_from_pdf(pdf_path):
    try:
        # Extract embedded text if available
        reader = PdfReader(pdf_path)
        embedded_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        if embedded_text.strip():
            return embedded_text

        # Otherwise, use OCR on images from the PDF
        images = convert_from_path(pdf_path)
        all_text = []
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, config='--psm 6')
            all_text.append(text)
        return "\n".join(all_text)
    except Exception as e:
        return f"Error processing PDF: {e}"


# OCR for DOCX
def ocr_from_docx(docx_path):
    doc = Document(docx_path)
    all_text = [p.text for p in doc.paragraphs]
    return "\n".join(all_text)


# OCR from URL
def ocr_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        temp_file = "temp_downloaded_file"
        with open(temp_file, "wb") as f:
            f.write(response.content)
        return ocr_from_file(temp_file)
    else:
        raise ValueError("Failed to fetch the file from the URL!")


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


# Generate PDF from Text
def generate_pdf(text, output_path="output.pdf"):
    c = canvas.Canvas(output_path)
    c.drawString(50, 800, "OCR Output:")
    text_lines = text.split("\n")
    y = 780
    for line in text_lines:
        if y < 50:  # Create new page if content exceeds
            c.showPage()
            y = 800
        c.drawString(50, y, line)
        y -= 15
    c.save()


# Streamlit Web App
def main():
    st.title("Advanced OCR System")
    st.write("Upload a file or provide a URL for OCR processing.")

    uploaded_file = st.file_uploader("Upload your file here", type=['png', 'jpg', 'jpeg', 'pdf', 'docx'])
    url_input = st.text_input("Or provide a file URL here")

    if uploaded_file or url_input:
        try:
            if uploaded_file:
                file_path = uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            elif url_input:
                st.text("Downloading the file...")
                file_path = "temp_url_file"
                response = requests.get(url_input)
                with open(file_path, "wb") as f:
                    f.write(response.content)

            # Perform OCR
            st.text("Performing OCR...")
            result = ocr_from_file(file_path)
            st.text_area("Extracted Text", result, height=300)

            # Copy Button
            st.button("Copy Text", on_click=lambda: st.write("Copied to clipboard!"))

            # Convert to PDF Button
            if st.button("Convert to PDF"):
                generate_pdf(result, "ocr_output.pdf")
                with open("ocr_output.pdf", "rb") as pdf_file:
                    st.download_button("Download PDF", pdf_file, file_name="ocr_output.pdf")
        except Exception as e:
            st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
