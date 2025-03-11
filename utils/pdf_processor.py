import pdfplumber
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    logger.info(f"Extracting text from PDF: {pdf_path}")
    extracted_text = ""
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Process each page
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                extracted_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                
                # Extract tables if any (might contain structured shipping info)
                tables = page.extract_tables()
                if tables:
                    extracted_text += "\n\n--- Tables ---\n\n"
                    for i, table in enumerate(tables):
                        extracted_text += f"\n--- Table {i+1} ---\n"
                        for row in table:
                            # Filter out None values and convert to string
                            row_text = " | ".join([str(cell) if cell is not None else "" for cell in row])
                            extracted_text += f"{row_text}\n"
        
        logger.info(f"Successfully extracted text from PDF ({len(extracted_text)} characters)")
        return extracted_text
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def preprocess_text(text):
    """
    Preprocess extracted text to make it more suitable for LLM processing.
    
    Args:
        text (str): Raw text extracted from PDF
        
    Returns:
        str: Preprocessed text
    """
    # Remove excessive whitespace
    processed_text = ' '.join(text.split())
    
    # Replace common OCR errors or formatting issues
    replacements = {
        '|': ' | ',  # Add spaces around pipe characters for better readability
        '\n\n\n+': '\n\n',  # Replace multiple newlines with just two
    }
    
    for old, new in replacements.items():
        processed_text = processed_text.replace(old, new)
    
    return processed_text
