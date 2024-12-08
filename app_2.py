import os
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import cv2
import numpy as np
import streamlit as st
import requests
from io import BytesIO
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pyttsx3
from datetime import datetime

# Enhanced Preprocessing for Images
def enhanced_preprocess_image(image_path):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Contrast(image)
    image_enhanced = enhancer.enhance(2)  # Increase contrast
    image_gray = image_enhanced.convert("L")  # Convert to grayscale
    image_filtered = image_gray.filter(ImageFilter.SHARPEN)  # Sharpen the image
    return image_filtered

# Enhanced OCR for Images
def enhanced_ocr_from_image(image_path):
    processed_image = enhanced_preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_image, config="--oem 3 --psm 6 -l eng")
    return text

# OCR for PDFs
def ocr_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        embedded_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        if embedded_text.strip():
            return embedded_text
        images = convert_from_path(pdf_path)
        all_text = [pytesseract.image_to_string(img, config="--psm 6") for img in images]
        return "\n".join(all_text)
    except Exception as e:
        return f"Error processing PDF: {e}"

# OCR for DOCX
def ocr_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join(p.text for p in doc.paragraphs)

# Unified OCR Function with Enhanced Image OCR
def ocr_from_file(file_path):
    extension = os.path.splitext(file_path)[-1].lower()
    if extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        return enhanced_ocr_from_image(file_path)
    elif extension == '.pdf':
        return ocr_from_pdf(file_path)
    elif extension == '.docx':
        return ocr_from_docx(file_path)
    else:
        return "Unsupported file format!"

# Generate PDF with Formatting Options
def generate_pdf(text, font="Helvetica", font_size=12, font_color=(0, 0, 0), output_path="output.pdf"):
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setFont(font, font_size)
    c.setFillColorRGB(*[x / 255 for x in font_color])  # Convert RGB to fraction
    y = 750
    for line in text.splitlines():
        if y < 50:  
            c.showPage()
            y = 750
            c.setFont(font, font_size)
            c.setFillColorRGB(*[x / 255 for x in font_color])
        c.drawString(50, y, line)
        y -= 15
    c.save()

# Text-to-Speech Function
def read_aloud(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Streamlit App
def main():
    st.title("Advanced OCR System")
    st.write("Upload a file or provide a URL for OCR processing.")

    # Display Current Date and Time
    current_time = datetime.now().strftime("%A, %B %d, %Y - %I:%M:%S %p")
    st.sidebar.markdown(f"### {current_time}")

    uploaded_file = st.file_uploader("Upload your file here", type=['png', 'jpg', 'jpeg', 'pdf', 'docx'])
    url_input = st.text_input("Or provide a file URL here")

    font_options = st.sidebar.selectbox("Choose Font Style", ["Helvetica", "Courier", "Times-Roman"])
    font_size = st.sidebar.slider("Font Size", 10, 30, 12)
    font_color = st.sidebar.color_picker("Font Color", "#000000")

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

            st.text("Performing OCR...")
            result = ocr_from_file(file_path)
            st.text_area("Extracted Text", result, height=300)

            if st.button("Read Aloud"):
                read_aloud(result)

            if st.button("Convert to PDF"):
                rgb_color = tuple(int(font_color[i:i+2], 16) for i in (1, 3, 5))  # Hex to RGB
                generate_pdf(result, font_options, font_size, rgb_color, "ocr_output.pdf")
                with open("ocr_output.pdf", "rb") as pdf_file:
                    st.download_button("Download PDF", pdf_file, file_name="ocr_output.pdf")
        except Exception as e:
            st.error(f"Error: {e}")

    # Footer
    st.markdown('<p style="position: fixed; bottom: 10px; right: 10px; font-size: small; font-weight: bold;">Aditya</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
