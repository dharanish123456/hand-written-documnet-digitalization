import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Azure API configuration
AZURE_OCR_KEY = os.environ.get("AZURE_OCR_KEY", "")
AZURE_OCR_ENDPOINT = os.environ.get("AZURE_OCR_ENDPOINT", "")

AZURE_TRANSLATOR_KEY = os.environ.get("AZURE_TRANSLATOR_KEY", " ")
AZURE_TRANSLATOR_ENDPOINT = os.environ.get("AZURE_TRANSLATOR_ENDPOINT", "")
AZURE_TRANSLATOR_REGION = os.environ.get("AZURE_TRANSLATOR_REGION", "centralindia")

AZURE_SPEECH_KEY = os.environ.get("AZURE_SPEECH_KEY", "OL")
AZURE_SPEECH_REGION = os.environ.get("AZURE_SPEECH_REGION", "centralindia")

# Path configurations
WKHTMLTOPDF_PATH = os.environ.get("WKHTMLTOPDF_PATH", r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

# Language mapping
LANGUAGES = {
    "English": "en", "Tamil": "ta", "Hindi": "hi", "French": "fr", "German": "de",
    "Spanish": "es", "Chinese": "zh", "Arabic": "ar", "Japanese": "ja", "Korean": "ko",
    "Portuguese": "pt", "Russian": "ru", "Italian": "it", "Dutch": "nl", "Turkish": "tr"
}