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
from translate import Translator  # Replacing googletrans
#from googletrans import Translator  # Updated to use googletrans 4.0.0-rc1
from pdf2image import convert_from_path

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
        
        # Default to a female voice if available
        female_voices = [v for v in voices if "female" in v.name.lower()]
        if female_voices:
            engine.setProperty('voice', female_voices[0].id)
        
        engine.setProperty('rate', 200)  # Fixed rate for simplicity
        
        # Split long text into manageable chunks
        max_length = 200
        text_chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        
        for chunk in text_chunks:
            engine.say(chunk)
        engine.runAndWait()
    
    threading.Thread(target=tts, daemon=True).start()

####################################################################################################################
# Auto generated & my added functions
# Unified OCR
def unified_ocr(image_path):
    if os.path.isfile(image_path):
        return perform_ocr(image_path,)
    else:
        return "Invalid file path!"
    

# Unified Image Preprocessing
def unified_preprocess_image(image_path):
    if os.path.isfile(image_path):
        return preprocess_image(image_path)
    else:
        return "Invalid file path!"

# Unified Read-Aloud
def unified_read_aloud(text):
    read_text_aloud(text)



# Unified Create PDF
def unified_create_pdf(text, output_path):
    if os.path.isdir(output_path):
        return create_pdf(text, output_path)
    else:
        return "Invalid output path!"

# Unified Convert to Word
def unified_convert_to_word(text, output_path):
    if os.path.isdir(output_path):
        return create_word_doc(text, output_path)
    else:
        return "Invalid output path!"


# Unified Translation
def unified_translation(text, language):
    return translate_text(text, language)

# Unified Translation
def translate_text(text, language):
    translator = Translator()
    translation = translator.translate(text, dest=language)
    return translation.text

# Unified Translation
def unified_translation_file(file_path, language):
    if os.path.isfile(file_path):
        return perform_ocr(file_path, language)
    else:
        return "Invalid file path!"

# Unified OCR from URL
def unified_ocr_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return perform_ocr(BytesIO(response.content) )
        else:
            return f"Failed to fetch the file from the URL: {response.status_code}"
    except Exception as e:
        return f"Error fetching the file from the URL: {e}"
    except Exception as e:
        return f"Error fetching the file from the URL: {e}"
    except Exception as e:
        return f"Error processing the file: {e}"
    except Exception as e:
        return f"Error processing the file: {e}"
    except Exception as e:
        return f"Error processing the file: {e}"
    except Exception as e:
        return f"Error processing the file: {e}"


# Unified OCR from File
def unified_ocr_from_file(file_path):
    if os.path.isfile(file_path):
        return perform_ocr(file_path,)
    else:
        return "Invalid file path!"

# Unified OCR from URL & Translation
def unified_ocr_url_translation(url, language):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            text = perform_ocr(BytesIO(response.content), language)
            return unified_translation(text, language)
        else:
            return f"Failed to fetch the file from the URL: {response.status_code}"
    except Exception as e:
        return f"Error fetching the file from the URL: {e}"
    except Exception as e:
        return f"Error processing the file: {e}"


# Unified OCR from File & Translation
def unified_ocr_file_translation(file_path, language):
    if os.path.isfile(file_path):
        text = perform_ocr(file_path, language)
        return unified_translation(text, language)
    else:
        return "Invalid file path!"
                    

# Unified OCR from URL & Translation & Save as PDF
def unified_ocr_url_translation_save_pdf(url, language, pdf_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            text = perform_ocr(BytesIO(response.content), language)
            formatted_text = unified_translation(text, language)
            return unified_create_pdf(formatted_text, pdf_path)
        else:
            return f"Failed to fetch the file from the URL: {response.status_code}"
    except Exception as e:
        return f"Error fetching the file from the URL: {e}"
    except Exception as e:
        return f"Error processing the file: {e}"


# Unified OCR from File & Translation & Save as PDF
def unified_ocr_file_translation_save_pdf(file_path, language, pdf_path):
    if os.path.isfile(file_path):
        text = perform_ocr(file_path, language)
        formatted_text = unified_translation(text, language)
        return unified_create_pdf(formatted_text, pdf_path)
    else:
        return "Invalid file path!"

# Unified OCR from URL & Translation & Save as Word
def unified_ocr_url_translation_save_word(url, language, word_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            text = perform_ocr(BytesIO(response.content), language)
            formatted_text = unified_translation(text, language)
            return unified_convert_to_word(formatted_text, word_path)
        else:
            return f"Failed to fetch the file from the URL: {response.status_code}"
    except Exception as e:
        return f"Error fetching the file from the URL: {e}"
    except Exception as e:
        return f"Error processing the file: {e}"


# Unified OCR from File & Translation & Save as Word
def unified_ocr_file_translation_save_word(file_path, language, word_path):
    if os.path.isfile(file_path):
        text = perform_ocr(file_path, language)
        formatted_text = unified_translation(text, language)
        return unified_convert_to_word(formatted_text, word_path)
    else:
        return "Invalid file path!"
    
########################################################################

# Specify the path to pdftoppm if needed

poppler_path = "/usr/local/bin"

def process_pdf(pdf_path, language="eng"):
    try:
        reader = PdfReader(pdf_path)
        embedded_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        
        if embedded_text.strip():
            return embedded_text
        else:
            # Use Poppler path if necessary
            images = convert_from_path(pdf_path, poppler_path=poppler_path)
            return "".join([pytesseract.image_to_string(img, config=f"--psm 6 -l {language}") for img in images])
    except Exception as e:
        return f"Error processing PDF: {e}"

################################################################################################################################################################

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
    language = st.sidebar.selectbox("OCR Language", ["English (eng)", "Hindi (hin)", "Russian (rus)", "French (fra)", "Chinese (chi_sim)"])
    language_code = language.split("(")[-1].strip(")")

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
            extracted_text = perform_ocr(file_path, language=language_code)
            editable_text = st.text_area("Extracted Text", value=extracted_text, height=300)

            # Read Aloud
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
            target_language = st.selectbox("Translate to", [
                "Hindi (hi)", "Sanskrit (sa)", "Punjabi (pa)", "Marathi (mr)", 
                "Russian (ru)", "French (fr)", "Chinese (zh-CN)"
            ])

            if st.button("Translate"):
                translator = Translator()
                try:
                    translated_text = translator.translate(editable_text, dest=target_language.split("(")[-1].strip(")")).text
                    st.text_area("Translated Text", value=translated_text, height=300)
                except Exception as e:
                    st.error(f"Translation Error: {e}")

            st.markdown(
            '<p style="position: fixed; bottom: 10px; right: 10px; font-size: small; font-weight: bold;">Aditya</p>',
            unsafe_allow_html=True
            )

        ################################################################
        # auto-generated
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

            # Clean up temporary files
            try:
                os.remove(file_path)
                os.remove("formatted_text.pdf")
                os.remove("formatted_text.docx")
                os.remove("formatted_text.txt")
            except Exception as e:
                st.warning(f"Error cleaning up temporary files: {e}")
                st.stop()

                # Translate Error Handling
                if "Translation Error" in str(e):
                    st.stop()
                    translator = Translator()
                    try:
                        translated_text = translator.translate(extracted_text, dest=target_language.split("(")[-1].strip(")")).text
                        st.text_area("Translated Text", value=translated_text, height=300)
                    except Exception as e:
                        st.error(f"Translation Error: {e}")

            else:
                st.info("Please upload a file or enter a URL.")
                st.stop()
        #----------------------------------------------------------------

# Run the app


if __name__ == "__main__":
    main()
