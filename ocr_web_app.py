# 2nd try
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from docx import Document
import cv2
import numpy as np
import streamlit as st
import requests
from io import BytesIO

# Helper Function: Preprocess Image
def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    # Additional noise removal and sharpening for better OCR
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    processed = cv2.GaussianBlur(processed, (5, 5), 0)
    return processed

# OCR for Images
def ocr_from_image(image_path):
    image = preprocess_image(image_path)
    text = pytesseract.image_to_string(image, config='--psm 6')
    return text

# OCR for PDFs
def ocr_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    all_text = []
    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image, config='--psm 6')
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

# OCR from URL
def ocr_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        file_data = BytesIO(response.content)
        with open("temp_download", "wb") as f:
            f.write(file_data.read())
        return ocr_from_file("temp_download")
    else:
        raise ValueError("Failed to fetch the file from the URL!")

# Streamlit Web App
def main():
    st.title("Advanced OCR System")
    st.write("Upload a file or provide a URL for OCR processing.")

    uploaded_file = st.file_uploader("Upload your file here", type=['png', 'jpg', 'jpeg', 'pdf', 'docx'])
    url_input = st.text_input("Or provide a file URL here")

    if uploaded_file:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {uploaded_file.name}")
        st.text("Performing OCR...")
        result = ocr_from_file(uploaded_file.name)
        st.text_area("Extracted Text", result, height=300)

    elif url_input:
        try:
            st.text("Downloading and processing...")
            result = ocr_from_url(url_input)
            st.text_area("Extracted Text", result, height=300)
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
