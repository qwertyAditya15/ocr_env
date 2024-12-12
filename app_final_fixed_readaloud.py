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


# Enhanced Image Preprocessing
def preprocess_image(image_path):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.convert("L")
    image = image.filter(ImageFilter.SHARPEN)
    return image


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

# Enhanced Read-Aloud with Voice and Speed Control
def read_text_aloud(text, voice="Default", rate=200):
    def tts():
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        # Filter only female voices
        female_voices = [v for v in voices if "female" in v.name.lower()]
        if voice != "Default":
            for v in female_voices:
                if voice.lower() in v.name.lower():
                    engine.setProperty('voice', v.id)
                    break
        elif female_voices:
            # Default to the first female voice if available
            engine.setProperty('voice', female_voices[0].id)
        
        engine.setProperty('rate', rate)
        
        # Split long text into manageable chunks for speech synthesis
        max_length = 200  # Approximate max characters per chunk
        text_chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        
        for chunk in text_chunks:
            engine.say(chunk)
        engine.runAndWait()
    
    # Use a thread to avoid blocking the UI
    threading.Thread(target=tts, daemon=True).start()
    threading.Thread(target=tts, daemon=True).start()


# Streamlit App
def main():
    st.title("Advanced OCR with Enhanced Formatting")
    st.sidebar.title("Formatting Options")
    font = st.sidebar.selectbox("Font Style", [
        "Helvetica", "Courier", "Times-Roman", "Arial",
        "Verdana", "Georgia", "Comic Sans MS"
    ])
    size = st.sidebar.slider("Font Size", 10, 50, 12)
    color = st.sidebar.color_picker("Pick a Color", "#000000")
    bold = st.sidebar.checkbox("Bold")
    underline = st.sidebar.checkbox("Underline")

    # Extract RGB from HEX color
    color_rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))

    uploaded_file = st.file_uploader("Upload your file", type=["png", "jpg", "jpeg", "pdf"])
    url = st.text_input("Or enter the file URL")

    if uploaded_file or url:
        try:
            if uploaded_file:
                file_path = uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            elif url:
                response = requests.get(url)
                file_path = url.split("/")[-1]
                with open(file_path, "wb") as f:
                    f.write(response.content)

            st.text("Performing OCR...")
            extracted_text = perform_ocr(file_path)
            st.text_area("Extracted Text", value=extracted_text, height=300)

            # Read Aloud Options
            voice_choice = st.sidebar.selectbox("Select Voice", [
                "Default", "Male", "Female", "Child", "Narrator"
            ])
            speed = st.sidebar.slider("Speech Speed (WPM)", 100, 300, 200)
            
            if st.button("Read Aloud"):
                read_text_aloud(extracted_text, voice=voice_choice, rate=speed)

            if st.button("Replay"):
                read_text_aloud(extracted_text, voice=voice_choice, rate=speed)

            # Save and Download Options
            if st.button("Save Changes"):
                edited_text = st.text_area("Edit Text", value=extracted_text, height=300)
                extracted_text = edited_text
                st.success("Changes saved!")

            if st.button("Download PDF"):
                pdf_path = create_pdf(extracted_text, font, size, color_rgb, bold, underline)
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", f, file_name="updated_text.pdf")

            if st.button("Convert to TXT"):
                txt_path = "formatted_text.txt"
                with open(txt_path, "w") as f:
                    f.write(extracted_text)
                with open(txt_path, "rb") as f:
                    st.download_button("Download TXT", f, file_name="formatted_text.txt")

            if st.button("Convert to Word"):
                word_path = create_word_doc(extracted_text)
                with open(word_path, "rb") as f:
                    st.download_button("Download Word", f, file_name="formatted_text.docx")

        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown(
        '<p style="position: fixed; bottom: 10px; right: 200px; font-size: 25px; font-weight: bold;">Aditya</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
