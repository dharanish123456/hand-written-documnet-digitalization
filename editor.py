import streamlit as st
import fitz  # PyMuPDF
from streamlit_quill import st_quill
import logging
from utils import generate_pdf, generate_word, generate_image, generate_markdown, generate_text
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = "\n".join([page.get_text("text") for page in doc])
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def editor_page():
    st.title("Document Editor (MS Word-Like)")

    st.subheader("Recent Documents")
    if "recent_documents" in st.session_state and st.session_state.recent_documents:
        for doc in st.session_state.recent_documents:
            with st.expander(f"{doc['source']} - {doc['timestamp']}"):
                st.text_area("Text Preview", doc["text"][:500] + "..." if len(doc["text"]) > 500 else doc["text"], height=150, disabled=True)
                if st.button("Load in Editor", key=f"load_{doc['timestamp']}"):
                    st.session_state.editor_text = doc["text"]
                    st.rerun()
    else:
        st.info("No recent documents found. Process some documents in Image to Text or Voice to Text to see them here.")

    uploaded_pdf = st.file_uploader("Upload a PDF to Edit", type=["pdf"])
    
    if uploaded_pdf:
        with st.spinner("Extracting text from PDF..."):
            extracted_text = extract_text_from_pdf(uploaded_pdf)
            if not extracted_text:
                st.warning("No text could be extracted from the PDF. It might be scanned or image-based.")
    else:
        extracted_text = st.session_state.get("editor_text", "")

    st.subheader("Edit the Document")
    text = st_quill(value=extracted_text, placeholder="Start typing here...", html=True)

    # Store processed document in session state for recent documents
    if text and not text.isspace():
        if "recent_documents" not in st.session_state:
            st.session_state.recent_documents = []
        st.session_state.recent_documents.append({
            "text": text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Editor"
        })
        if len(st.session_state.recent_documents) > 5:
            st.session_state.recent_documents.pop(0)

    st.subheader("Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox("Select file format", ["PDF", "Word", "Image", "Markdown", "Text"])
    
    with col2:
        pdf_header = None
        pdf_footer = None
        if export_format == "PDF":
            with st.expander("PDF Customization"):
                pdf_header = st.text_input("Header (e.g., Document Title)", "")
                pdf_footer = st.text_input("Footer (e.g., Page Number or Date)", "")
        
        if st.button("Download"):
            try:
                if not text or text.isspace():
                    st.warning("Please add some content before downloading.")
                    return
                
                with st.spinner(f"Generating {export_format} document..."):
                    if export_format == "PDF":
                        pdf_bytes = generate_pdf(text, header=pdf_header, footer=pdf_footer)
                        st.download_button("Download PDF", pdf_bytes, "edited_document.pdf", "application/pdf")
                    elif export_format == "Word":
                        word_bytes = generate_word(text)
                        st.download_button("Download Word", word_bytes, "edited_document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    elif export_format == "Image":
                        image_bytes = generate_image(text)
                        st.download_button("Download PNG", image_bytes, "edited_document.png", "image/png")
                    elif export_format == "Markdown":
                        md_bytes = generate_markdown(text)
                        st.download_button("Download Markdown", md_bytes, "edited_document.md", "text/markdown")
                    else:  # Text
                        txt_bytes = generate_text(text)
                        st.download_button("Download Text", txt_bytes, "edited_document.txt", "text/plain")
            except Exception as e:
                st.error(f"Error generating {export_format}: {str(e)}")