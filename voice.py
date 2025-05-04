import streamlit as st
import os
import logging
import time
import azure.cognitiveservices.speech as speechsdk
import requests
from datetime import datetime
from utils import generate_pdf, generate_word, generate_image
from config import AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_ENDPOINT, AZURE_TRANSLATOR_REGION, LANGUAGES

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Azure-supported language codes
AZURE_SUPPORTED_LANGUAGES = {
    "English": "en-US",
    "Hindi": "hi-IN",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
}

def transcribe_audio(file_path, language="en-US"):
    """
    Transcribe a short audio file using Azure Speech recognize_once().
    Best for files under ~2 minutes.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found - {file_path}"

    supported_formats = ['.wav', '.ogg', '.mp3', '.m4a']
    if not any(file_path.lower().endswith(fmt) for fmt in supported_formats):
        return f"Error: Unsupported format. Supported: {', '.join(supported_formats)}."

    try:
        subscription_key = os.getenv("AZURE_SPEECH_KEY")
        region = os.getenv("AZURE_SPEECH_REGION")

        if not subscription_key or not region:
            return "Error: Missing Azure Speech credentials."

        speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
        speech_config.speech_recognition_language = language

        audio_config = speechsdk.audio.AudioConfig(filename=file_path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        result = speech_recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return "No speech recognized. Please check your audio."
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            return f"Recognition canceled: {cancellation_details.reason}. Error details: {cancellation_details.error_details}"
        else:
            return "Error: Unknown recognition result."

    except Exception as e:
        return f"Exception during transcription: {str(e)}"

def translate_text_azure(text, target_lang="en"):
    """Translate text using Azure Translator API."""
    try:
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
            "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
            "Content-Type": "application/json"
        }
        params = {"api-version": "3.0", "to": target_lang}
        body = [{"text": text}]
        response = requests.post(
            AZURE_TRANSLATOR_ENDPOINT + "/translate",
            headers=headers,
            params=params,
            json=body,
            timeout=30
        )
        response.raise_for_status()
        translated_text = response.json()[0]["translations"][0]["text"]
        return translated_text
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return f"Translation failed: {str(e)}"

def voice_page():
    """Streamlit page for voice-to-text conversion using Azure Speech Services."""
    st.title("🎙️ Voice to Text Converter")

    if "audio_file" not in st.session_state:
        st.session_state.audio_file = None
    if "recognized_text" not in st.session_state:
        st.session_state.recognized_text = ""
    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""

    st.subheader("Step 1: Upload Audio File")
    uploaded_file = st.file_uploader(
        "Upload an audio file (WAV, MP3, OGG, M4A)", 
        type=["wav", "mp3", "ogg", "m4a"],
        key="audio_uploader"
    )

    if uploaded_file:
        os.makedirs("temp_audio", exist_ok=True)
        file_path = f"temp_audio/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.audio_file = file_path
        st.subheader("Audio Playback")
        st.audio(uploaded_file, format=uploaded_file.type)

        st.subheader("Step 2: Convert to Text")
        transcription_language = st.selectbox(
            "Select transcription language",
            list(AZURE_SUPPORTED_LANGUAGES.keys()),
            index=list(AZURE_SUPPORTED_LANGUAGES.keys()).index("English")
        )
        transcription_lang_code = AZURE_SUPPORTED_LANGUAGES[transcription_language]

        if st.button("📝 Convert to Text"):
            with st.spinner("Transcribing audio..."):
                result = transcribe_audio(file_path, language=transcription_lang_code)
                if result and not result.startswith(("Error", "Recognition canceled", "No speech")):
                    st.session_state.recognized_text = result
                    st.success("Transcription completed!")
                else:
                    st.error(result)

    if st.session_state.recognized_text:
        st.subheader("Recognized Text")
        recognized_text = st.text_area(
            "You can edit the text if needed:",
            value=st.session_state.recognized_text,
            height=150
        )
        if recognized_text != st.session_state.recognized_text:
            st.session_state.recognized_text = recognized_text

        st.subheader("Step 3: Translate (Optional)")
        enable_translation = st.checkbox("Translate to another language", value=False)

        if enable_translation:
            target_language = st.selectbox(
                "Select target language",
                list(LANGUAGES.keys()),
                key="translate_language"
            )
            target_language_code = LANGUAGES[target_language]

            if st.button("🌎 Translate Text"):
                with st.spinner(f"Translating to {target_language}..."):
                    translated = translate_text_azure(
                        st.session_state.recognized_text,
                        target_language_code
                    )
                    if translated.startswith("Translation failed"):
                        st.error(translated)
                    else:
                        st.session_state.translated_text = translated
                        st.success("Translation completed!")

            if st.session_state.translated_text:
                st.text_area(
                    "Translated Text",
                    value=st.session_state.translated_text,
                    height=150
                )

        final_text = (st.session_state.translated_text 
                      if enable_translation and st.session_state.translated_text 
                      else st.session_state.recognized_text)

        st.subheader("Step 4: Download Your Result")
        export_format = st.selectbox("Choose Export Format", ["PDF", "Word", "Image"])

        if st.button("⬇️ Download"):
            try:
                with st.spinner(f"Generating {export_format}..."):
                    if export_format == "PDF":
                        output = generate_pdf(final_text)
                        st.download_button(
                            "Download PDF",
                            output,
                            "voice_output.pdf",
                            "application/pdf"
                        )
                    elif export_format == "Word":
                        output = generate_word(final_text)
                        st.download_button(
                            "Download Word",
                            output,
                            "voice_output.docx",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    else:
                        output = generate_image(final_text)
                        st.download_button(
                            "Download Image",
                            output,
                            "voice_output.png",
                            "image/png"
                        )
            except Exception as e:
                st.error(f"Failed to generate {export_format}: {str(e)}")

        # File Management
        with st.expander("Cleanup Temporary Files"):
            if st.button("Delete Uploaded Audio"):
                try:
                    if st.session_state.audio_file and os.path.exists(st.session_state.audio_file):
                        os.remove(st.session_state.audio_file)
                        st.session_state.audio_file = None
                        st.session_state.recognized_text = ""
                        st.session_state.translated_text = ""
                        st.success("Audio file deleted successfully!")
                except Exception as e:
                    st.error(f"Failed to delete audio file: {str(e)}")

if __name__ == "__main__":
    voice_page()
