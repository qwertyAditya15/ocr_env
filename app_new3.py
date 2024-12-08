import os
import requests
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from datetime import datetime
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st
import pytesseract
import pyttsx3
import threading
from googletrans import Translator

# Enhanced Image Preprocessing
def preprocess_image(image_path):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.convert("L")
    image = image.filter(ImageFilter.SHARPEN)
    return image

# Unified OCR
def perform_ocr(file_path, language="eng"):
    extension = os.path.splitext(file_path)[-1].lower()
    if extension in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        image = preprocess_image(file_path)
        return pytesseract.image_to_string(image, config=f"--oem 3 --psm 6 -l {language}")
    elif extension == ".pdf":
        return process_pdf(file_path, language)
    else:
        return "Unsupported file format!"

# OCR for PDFs
def process_pdf(pdf_path, language="eng"):
    try:
        reader = PdfReader(pdf_path)
        embedded_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        
        if embedded_text.strip():
            return embedded_text
        else:
            images = convert_from_path(pdf_path)
            return "".join([pytesseract.image_to_string(img, config=f"--psm 6 -l {language}") for img in images])
    except Exception as e:
        return f"Error processing PDF: {e}"

# Create PDF from Text
def create_pdf(text, font, size, color, bold, underline):
    output_path = "formatted_text.pdf"
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setFont(font, size)
    c.setFillColorRGB(color[0] / 255, color[1] / 255, color[2] / 255)
    y = 750
    for line in text.splitlines():
        c.drawString(50, y, line)
        y -= size + 5
    c.save()
    return output_path

# Convert to Word
def create_word_doc(text):
    doc = Document()
    doc.add_paragraph(text)
    output_path = "formatted_text.docx"
    doc.save(output_path)
    return output_path

# Enhanced Read-Aloud with Default Female Voice
def read_text_aloud(text):
    def tts():
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        female_voices = [v for v in voices if "female" in v.name.lower()]
        if female_voices:
            engine.setProperty('voice', female_voices[0].id)
        engine.setProperty('rate', 200)
        
        for chunk in [text[i:i+200] for i in range(0, len(text), 200)]:
            engine.say(chunk)
        engine.runAndWait()
    
    threading.Thread(target=tts, daemon=True).start()

# Streamlit App
def main():
    st.title("Advanced OCR with Enhanced Formatting")
    st.sidebar.title("Formatting Options")
    font = st.sidebar.selectbox("Font Style", ["Helvetica", "Courier", "Times-Roman", "Arial", "Verdana", "Georgia"])
    size = st.sidebar.slider("Font Size", 10, 50, 12)
    color = st.sidebar.color_picker("Pick a Color", "#000000")
    bold = st.sidebar.checkbox("Bold")
    underline = st.sidebar.checkbox("Underline")
    color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

    uploaded_file = st.file_uploader("Upload your file", type=["png", "jpg", "jpeg", "pdf"])
    language = st.sidebar.selectbox("OCR Language", ["English (eng)", "Hindi (hin)", "Russian (rus)", "French (fra)", "Chinese (chi_sim)"])
    language_code = language.split("(")[-1].strip(")")

    if uploaded_file:
        file_path = uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.text("Performing OCR...")
        extracted_text = perform_ocr(file_path, language=language_code)
        editable_text = st.text_area("Extracted Text", value=extracted_text, height=300)

        # Read Aloud Button
        if st.button("Read Aloud"):
            read_text_aloud(editable_text)

        # Save and Download Options
        if st.button("Download Updated PDF"):
            pdf_path = create_pdf(editable_text, font, size, color_rgb, bold, underline)
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", f, file_name="updated_text.pdf")

        if st.button("Convert to TXT"):
            txt_path = "formatted_text.txt"
            with open(txt_path, "w") as f:
                f.write(editable_text)
            with open(txt_path, "rb") as f:
                st.download_button("Download TXT", f, file_name="formatted_text.txt")

        if st.button("Convert to Word"):
            word_path = create_word_doc(editable_text)
            with open(word_path, "rb") as f:
                st.download_button("Download Word", f, file_name="formatted_text.docx")

        # Translation Panel
        st.header("Translation Panel")
        target_language = st.selectbox("Translate to", ["Hindi (hi)", "Sanskrit (sa)", "Punjabi (pa)", "Marathi (mr)", "Russian (ru)", "French (fr)", "Chinese (zh-CN)"])
        translator = Translator()
        if st.button("Translate"):
            try:
                translated_text = translator.translate(editable_text, dest=target_language.split("(")[-1].strip(")")).text
                st.text_area("Translated Text", value=translated_text, height=300)
            except Exception as e:
                st.error(f"Translation Error: {e}")

if __name__ == "__main__":
    main()
