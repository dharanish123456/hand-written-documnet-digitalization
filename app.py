import streamlit as st
import os
from home import home_page
from voice import voice_page
from editor import editor_page

def create_env_file():
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Azure API Keys\n")
            f.write("AZURE_OCR_KEY=3ut5ZPB9B8jxFuD1zGlhO6RkOLOmIvhtBEaavveQWQZ6BRwPxVPbJQQJ99BCACGhslBXJ3w3AAAFACOGpAa7\n")
            f.write("AZURE_OCR_ENDPOINT=https://dharanish.cognitiveservices.azure.com/\n")
            f.write("AZURE_TRANSLATOR_KEY= \n")
            f.write("AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/\n")
            f.write("AZURE_TRANSLATOR_REGION=centralindia\n")
            f.write("AZURE_SPEECH_KEY=SPGjIEgkJwKOhvEf6g55d1jGPhDH884kLz0ELBky9grmkggjUKxUJQQJ99BDACGhslBXJ3w3AAAYACOGyDOL\n")
            f.write("AZURE_SPEECH_REGION=centralindia\n")
            f.write("# Path configurations\n")
            f.write("WKHTMLTOPDF_PATH=C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe\n")

def setup_application():
    create_env_file()
    os.makedirs("styles", exist_ok=True)
    if not os.path.exists("styles/main.css"):
        with open("styles/main.css", "w") as f:
            f.write(""" 
            .stApp {
                background-color: #1a1a2e;
                color: #fff;
            }
            .hero {
                text-align: center;
                padding: 50px 0;
            }
            .hero h1 {
                font-size: 3rem;
                color: #fff;
            }
            .hero h1 span {
                color: #4CAF50;
            }
            .subtitle {
                font-size: 1.5rem;
                color: #ccc;
                margin-bottom: 40px;
            }
            .footer {
                text-align: center;
                margin-top: 50px;
                color: #999;
            }
            .feature-container {
                text-align: center;
                padding: 50px 0;
            }
            .feature-container h1 {
                font-size: 2.5rem;
                color: #fff;
            }
            .stButton>button {
                padding: 15px 30px;
                font-size: 1.2rem;
                border-radius: 10px;
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
                margin: 10px;
            }
            .stButton>button:hover {
                background-color: #388E3C;
            }
            .button-container {
                display: flex;
                justify-content: center;
                gap: 30px;
                margin-top: 10px;
                max-width: 900px;
                margin-left: auto;
                margin-right: auto;
            }
            .feature-image {
                border-radius: 10px;
                transition: transform 0.3s ease;
            }
            .feature-image:hover {
                transform: scale(1.05);
            }
            """)

def main():
    setup_application()
    st.set_page_config(page_title="DocDigitizer", layout="wide")

    # Load custom CSS
    with open("styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "Welcome"

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Welcome", "Image to Text", "Voice to Text", "Editor"])

    if page == "Welcome":
        st.markdown(""" 
            <div class="hero">
                <h1>Transform Documents with <span>AI</span></h1>
                <p class="subtitle">OCR, Speech-to-Text, and Export — All in One Place</p>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("About Us")
        st.markdown("""
            At DocDigitizer, we are passionate about revolutionizing how you interact with documents. Our mission is to harness cutting-edge artificial intelligence to simplify document processing, making it faster, more accurate, and accessible to everyone. Whether you're digitizing handwritten notes, transcribing audio, or editing complex documents, our platform empowers you with tools to streamline your workflow.

            Founded by a team of AI enthusiasts and software engineers, DocDigitizer combines Azure's powerful AI services with an intuitive interface. We prioritize user privacy, ensuring your data is processed securely and never stored. From small businesses to individual creators, we aim to support diverse needs with features like OCR, speech-to-text, and versatile export options (PDF, Word, Markdown, and more). Our vision is to make document management effortless, letting you focus on what matters most.

            Join us on this journey to transform the way the world handles documents!
        """)

        st.subheader("Our Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.image("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", caption="Image to Text (OCR)", use_column_width=True, output_format="PNG")
            if st.button("Learn More", key="ocr_learn"):
                st.info("Extract text from handwritten or scanned documents with our advanced Azure OCR technology.")
        
        with col2:
            st.image("https://images.unsplash.com/photo-1516321318423-f06f85e504b3", caption="Voice to Text", use_column_width=True, output_format="PNG")
            if st.button("Learn More", key="voice_learn"):
                st.info("Transcribe audio recordings into text effortlessly using AI-powered speech recognition.")
        
        with col3:
            st.image("https://images.unsplash.com/photo-1516321497487-e288fb19713f", caption="Document Editor", use_column_width=True, output_format="PNG")
            if st.button("Learn More", key="editor_learn"):
                st.info("Edit documents with a rich-text editor and export in multiple formats, including PDF and Word.")

        st.markdown(""" 
            <div class="footer">
                <p>Your data is never stored. Processed securely via Azure AI.</p>
            </div>
        """, unsafe_allow_html=True)
    
    elif page == "Image to Text":
        home_page()
    elif page == "Voice to Text":
        voice_page()
    elif page == "Editor":
        editor_page()

if __name__ == "__main__":
    main()