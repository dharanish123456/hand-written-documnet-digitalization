import pdfkit
from docx import Document
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
import logging
from config import WKHTMLTOPDF_PATH

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_pdfkit_config():
    """Get platform-independent pdfkit configuration"""
    if os.path.exists(WKHTMLTOPDF_PATH):
        return pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    else:
        logger.warning(f"wkhtmltopdf not found at {WKHTMLTOPDF_PATH}, using system PATH")
        return None

def generate_pdf(text, header=None, footer=None):
    """Generate PDF from HTML text with optional header and footer"""
    try:
        config = get_pdfkit_config()
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
        }
        if header:
            options['header-center'] = header
            options['header-spacing'] = '5'
        if footer:
            options['footer-center'] = footer
            options['footer-spacing'] = '5'
        
        html_content = f"""
        <html>
            <head><meta charset='UTF-8'></head>
            <body style='font-family: Arial, sans-serif;'>{text}</body>
        </html>
        """
        pdf_bytes = pdfkit.from_string(html_content, False, options=options, configuration=config)
        pdf_buffer = BytesIO(pdf_bytes)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise Exception(f"Failed to generate PDF: {str(e)}")

def generate_word(text):
    """Generate Word document from text"""
    try:
        doc = Document()
        doc.add_paragraph(text)
        word_buffer = BytesIO()
        doc.save(word_buffer)
        word_buffer.seek(0)
        return word_buffer.getvalue()
    except Exception as e:
        logger.error(f"Error generating Word document: {str(e)}")
        raise Exception(f"Failed to generate Word document: {str(e)}")

def generate_image(text, width=800, height=600, font_size=20):
    """Generate image from text with improved formatting"""
    try:
        background_color = (255, 255, 255)
        text_color = (0, 0, 0)
        padding = 20
        
        img = Image.new("RGB", (width, height), color=background_color)
        d = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        
        lines = []
        words = text.split()
        current_line = words[0] if words else ""
        
        for word in words[1:]:
            test_line = current_line + " " + word
            test_width = d.textlength(test_line, font=font)
            
            if test_width < (width - 2 * padding):
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
                
        if current_line:
            lines.append(current_line)
        
        y_position = padding
        for line in lines:
            d.text((padding, y_position), line, fill=text_color, font=font)
            y_position += font_size + 5
        
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        return img_buffer.getvalue()
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise Exception(f"Failed to generate image: {str(e)}")

def generate_markdown(text):
    """Generate Markdown file from text"""
    try:
        md_buffer = BytesIO(text.encode('utf-8'))
        md_buffer.seek(0)
        return md_buffer.getvalue()
    except Exception as e:
        logger.error(f"Error generating Markdown: {str(e)}")
        raise Exception(f"Failed to generate Markdown: {str(e)}")

def generate_text(text):
    """Generate plain text file from text"""
    try:
        txt_buffer = BytesIO(text.encode('utf-8'))
        txt_buffer.seek(0)
        return txt_buffer.getvalue()
    except Exception as e:
        logger.error(f"Error generating text file: {str(e)}")
        raise Exception(f"Failed to generate text file: {str(e)}")