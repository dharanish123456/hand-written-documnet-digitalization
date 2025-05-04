import streamlit as st
import requests
import os
import logging
import time
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from utils import generate_pdf, generate_word, generate_image, generate_markdown, generate_text
from config import AZURE_OCR_KEY, AZURE_OCR_ENDPOINT, AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_ENDPOINT, AZURE_TRANSLATOR_REGION, LANGUAGES

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def preprocess_image(image_bytes):
    """Preprocess image to improve OCR accuracy"""
    try:
        image = Image.open(BytesIO(image_bytes))
        image = image.convert("L")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        image = image.filter(ImageFilter.SHARPEN)
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        output = BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        return image_bytes

def perform_ocr(image_bytes):
    """Perform OCR on image using Azure Read API"""
    try:
        processed_image = preprocess_image(image_bytes)
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_OCR_KEY,
            "Content-Type": "application/octet-stream"
        }
        read_url = f"{AZURE_OCR_ENDPOINT}/vision/v3.2/read/analyze"
        response = requests.post(read_url, headers=headers, data=processed_image, timeout=30)
        
        if response.status_code != 202:
            logger.error(f"Read API error: {response.status_code} - {response.text}")
            return f"OCR Failed: {response.status_code} - {response.text[:100]}..."
        
        operation_location = response.headers["Operation-Location"]
        for _ in range(10):
            response = requests.get(operation_location, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result["status"] == "succeeded":
                    extracted_text = "\n".join([
                        line["text"]
                        for page in result["analyzeResult"]["readResults"]
                        for line in page["lines"]
                    ])
                    return extracted_text if extracted_text else "No text detected."
                elif result["status"] == "failed":
                    logger.error("Read API failed")
                    return "OCR Failed: Read API processing error"
            time.sleep(3)
        return "OCR Failed: Timeout waiting for Read API results"
    except Exception as e:
        logger.error(f"Error in OCR processing: {str(e)}")
        return f"OCR Error: {str(e)}"

def translate_text(text, target_language_code):
    """Translate text using Azure Translator API"""
    try:
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
            "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
            "Content-Type": "application/json"
        }
        params = {"api-version": "3.0", "to": target_language_code}
        response = requests.post(
            f"{AZURE_TRANSLATOR_ENDPOINT}/translate",
            headers=headers,
            params=params,
            json=[{"text": text}],
            timeout=30
        )
        if response.status_code == 200:
            return response.json()[0]["translations"][0]["text"]
        else:
            logger.error(f"Translation API error: {response.status_code} - {response.text}")
            return f"Translation Failed: {response.status_code} - {response.text[:100]}..."
    except Exception as e:
        logger.error(f"Error in translation: {str(e)}")
        return f"Translation Error: {str(e)}"

def home_page():
    st.title("Handwritten Document Digitalization")

    uploaded_file = st.file_uploader("Upload a handwritten document", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        try:
            st.image(uploaded_file, caption="Uploaded Document", use_column_width=True)
            with st.spinner("Performing OCR on document..."):
                image_bytes = uploaded_file.read()
                extracted_text = perform_ocr(image_bytes)
                if extracted_text and not extracted_text.startswith("OCR Failed") and not extracted_text.startswith("OCR Error"):
                    st.success("OCR completed successfully!")
                else:
                    st.warning("OCR processing encountered issues. Try a higher quality image.")
            
            st.subheader("Recognized Text")
            text_area = st.text_area("Edit the extracted text if needed:", extracted_text, height=200)

            enable_translation = st.checkbox("Enable Translation", value=False)
            translated_text = text_area

            if enable_translation and text_area:
                with st.expander("Translation Options", expanded=True):
                    target_language = st.selectbox("Select language for translation", list(LANGUAGES.keys()))
                    if target_language != "English":
                        with st.spinner(f"Translating to {target_language}..."):
                            translated_text = translate_text(text_area, LANGUAGES[target_language])
                            if translated_text and not translated_text.startswith("Translation Failed") and not translated_text.startswith("Translation Error"):
                                st.success("Translation completed!")
                            else:
                                st.warning("Translation encountered issues.")
                    else:
                        translated_text = text_area
                    st.subheader("Translated Text")
                    st.write(translated_text)
            else:
                st.subheader("Final Text")
                st.write(translated_text)

            # Store processed document in session state for dashboard
            if "recent_documents" not in st.session_state:
                st.session_state.recent_documents = []
            st.session_state.recent_documents.append({
                "text": translated_text,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "Image to Text"
            })
            if len(st.session_state.recent_documents) > 5:
                st.session_state.recent_documents.pop(0)

            st.subheader("Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                export_format = st.selectbox("Select export format", ["PDF", "Word", "Image", "Markdown", "Text"])
            
            with col2:
                pdf_header = None
                pdf_footer = None
                if export_format == "PDF":
                    with st.expander("PDF Customization"):
                        pdf_header = st.text_input("Header (e.g., Document Title)", "")
                        pdf_footer = st.text_input("Footer (e.g., Page Number or Date)", "")
                
                if st.button("Download"):
                    try:
                        with st.spinner(f"Generating {export_format}..."):
                            if export_format == "PDF":
                                pdf_bytes = generate_pdf(translated_text, header=pdf_header, footer=pdf_footer)
                                st.download_button("Download PDF", pdf_bytes, "output.pdf", "application/pdf")
                            elif export_format == "Word":
                                word_bytes = generate_word(translated_text)
                                st.download_button("Download Word", word_bytes, "output.docx", 
                                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                            elif export_format == "Image":
                                image_bytes = generate_image(translated_text)
                                st.download_button("Download PNG", image_bytes, "output.png", "image/png")
                            elif export_format == "Markdown":
                                md_bytes = generate_markdown(translated_text)
                                st.download_button("Download Markdown", md_bytes, "output.md", "text/markdown")
                            else:  # Text
                                txt_bytes = generate_text(translated_text)
                                st.download_button("Download Text", txt_bytes, "output.txt", "text/plain")
                    except Exception as e:
                        st.error(f"Error generating {export_format}: {str(e)}")
                
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            logger.error(f"Error processing image: {str(e)}")