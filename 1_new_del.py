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
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import pyperclip

# Apply Gaussian Filter and Binarization (OpenCV)
def apply_gaussian_filter(image):
    return cv2.GaussianBlur(image, (5, 5), 0)

def preprocess_image_opencv(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = apply_gaussian_filter(image)
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return Image.fromarray(image)

# Apply Contrast Enhancement and Sharpening (PIL)
def preprocess_image_pil(image):
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.convert("L")
    image = image.filter(ImageFilter.SHARPEN)
    return image

# Unified Preprocessing Function
def preprocess_image(image_path):
    # Apply OpenCV-based preprocessing
    processed_image = preprocess_image_opencv(image_path)
    # Apply PIL-based post-processing
    processed_image = preprocess_image_pil(processed_image)
    return processed_image

# Unified OCR
def perform_ocr(file_path):
    extension = os.path.splitext(file_path)[-1].lower()
    if extension in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        image = preprocess_image(file_path)
        return pytesseract.image_to_string(image, config="--oem 3 --psm 6 -l eng")
    elif extension == ".pdf":
        return process_pdf(file_path)
    else:
        return "Unsupported file format!"

# OCR for PDFs
def process_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        embedded_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        if embedded_text.strip():
            return embedded_text
        else:
            images = convert_from_path(pdf_path)
            return "".join([pytesseract.image_to_string(img, config="--psm 6") for img in images])
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

# Enhanced Read-Aloud with Voice and Speed Control

# Global variable for the audio player
audio_player = None

# Function to read the text aloud
def read_text_aloud(text, voice="Default", rate=200):
    global audio_player

    # Stop the previous audio player
    if audio_player is not None:
        audio_player.stop()

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    # Set the voice and rate
    engine.setProperty("voice", voice)
    engine.setProperty("rate", rate)

    # Start reading the text aloud
    audio_player = engine.say(text)
    audio_player.runAndWait()

# Function to handle the replay button
def replay_read_aloud():
    global audio_player

    # Start reading the text aloud again
    audio_player.runAndWait()

# Function to handle the save button
def save_changes(text, format_type):
    if format_type == "PDF":
        create_pdf(text, "Helvetica", 12, [0, 0, 0], False, False)
    elif format_type == "Word":
        create_word_doc(text)
    elif format_type == "Text":
        with open("formatted_text.txt", "w") as f:
            f.write(text)

extracted_text = " "

# Function to handle the copy button
def copy_text():
    pyperclip.copy(extracted_text)

# Streamlit app
def main():
    st.title("OCR App")

    # File upload
    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "jpg", "jpeg", "png", "tiff"])
    if uploaded_file is not None:

        # Display the file name and type
        st.write(f"File name: {uploaded_file.name}")
        st.write(f"File type: {uploaded_file.type}")

        # Perform OCR
        if uploaded_file.type in [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/tiff",
            "image/bmp",
        ]:
            if uploaded_file.type == "application/pdf":
                extracted_text = perform_ocr(uploaded_file)
            else:
                image = Image.open(uploaded_file)
                image = preprocess_image(image)
                extracted_text = pytesseract.image_to_string(image, config="--oem 3 --psm 6 -l eng")

            # Display the extracted text
            st.write("Extracted Text:")
            st.write(extracted_text, unsafe_allow_html=True)

            # Read-aloud button
            read_aloud_button = st.button("Read Aloud")
            if read_aloud_button:
                voice_options = ["Default", "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"]
                voice_option = st.selectbox("Voice", voice_options)
                read_text_aloud(extracted_text, voice_option)

            # Replay button
            replay_button = st.button("Replay")
            if replay_button:
                replay_read_aloud()

            # Save button
            format_options = ["PDF", "Word", "Text"]
            format_option = st.selectbox("Save as", format_options)
            save_changes_button = st.button("Save Changes")
            if save_changes_button:
                save_changes(extracted_text, format_option)

            # Copy button
            copy_button = st.button("Copy Text")
            if copy_button:
                copy_text()

            # Make changes to the extracted text
            make_changes = st.text_area("Make changes to the extracted text", extracted_text, height=300)
            if make_changes != extracted_text:
                extracted_text = make_changes

        else:
            st.write("Unsupported file format!")

    else:
        st.write("Upload a file to get started!")

if __name__ == "__main__":
    main()