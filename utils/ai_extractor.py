import os
import re
import json
import logging
from anthropic import Anthropic
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def init_ai_client():
    """
    Initialize Anthropic AI client.
    """
    try:
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        return Anthropic(api_key=anthropic_key)
    except Exception as e:
        logger.error(f"Error initializing Anthropic client: {str(e)}")
        raise

def extract_json_from_text(text):
    """
    Attempt to extract a valid JSON object from text that might have extra content.
    
    Args:
        text (str): Text that may contain a JSON object
        
    Returns:
        dict: Extracted JSON object or None if extraction fails
    """
    # Try to find JSON between curly braces
    matches = re.findall(r'\{.*?\}', text, re.DOTALL)
    
    if matches:
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    # Try standard method to extract from markdown code blocks
    if "```json" in text:
        parts = text.split("```json")
        if len(parts) > 1:
            json_candidate = parts[1].split("```")[0].strip()
            try:
                return json.loads(json_candidate)
            except json.JSONDecodeError:
                pass
    
    if "```" in text:
        parts = text.split("```")
        if len(parts) > 1:
            json_candidate = parts[1].strip()
            try:
                return json.loads(json_candidate)
            except json.JSONDecodeError:
                pass
    
    return None

def extract_shipping_data(pdf_text):
    """
    Extract shipping information from PDF text using Anthropic AI.
    
    Args:
        pdf_text (str): Text extracted from the PDF
        
    Returns:
        dict: Extracted shipping information
    """
    logger.info("Sending request to Anthropic AI")
    
    try:
        client = init_ai_client()
        
        # Create system prompt
        system_prompt = """You are an AI assistant specialized in extracting shipping information from courier airway bills.
        
IMPORTANT: Your response must be a valid JSON object only, with no text before or after.
Do not include markdown code blocks or explanations."""

        # Create user prompt
        user_prompt = f"""Please extract the following information from this courier airway bill text and return it as a JSON object:
- Order ID
- Recipient Name
- Recipient Address
- Courier Name
- Tracking Number

If any field cannot be found, label it as "Not Found".

Here is the text from the courier airway bill:

{pdf_text}"""
        
        # Create the message with proper Anthropic format
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )
        
        # Extract and parse the response
        completion_text = message.content[0].text
        return parse_ai_response(completion_text)
        
    except Exception as e:
        logger.error(f"Anthropic extraction error: {str(e)}")
        raise

def parse_ai_response(text):
    """
    Parse the AI response to extract structured data.
    """
    try:
        # Try to parse directly as JSON
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from text
        extracted_data = extract_json_from_text(text)
        if extracted_data:
            return extracted_data
        
        # If no JSON found, parse text response
        logger.warning("Could not find valid JSON in response, attempting manual parsing")
        extracted_data = parse_text_response(text)
        
        # Ensure all required fields are present
        required_fields = ["Order ID", "Recipient Name", "Recipient Address", "Courier Name", "Tracking Number"]
        for field in required_fields:
            if field not in extracted_data:
                extracted_data[field] = "Not Found"
        
        return extracted_data

def parse_text_response(text):
    """
    Fallback method to parse non-JSON response into structured data.
    """
    extracted_data = {}
    field_patterns = {
        "Order ID": ["order id", "order number", "order #", "id"],
        "Recipient Name": ["recipient name", "receiver name", "consignee", "to:"],
        "Recipient Address": ["recipient address", "delivery address", "shipping address", "destination"],
        "Courier Name": ["courier name", "carrier", "shipping company", "delivery service"],
        "Tracking Number": ["tracking number", "tracking #", "awb", "airway bill", "tracking id"]
    }
    
    # Clean up text
    text = text.replace("```", "").strip()
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to find field labels and values
        for field, patterns in field_patterns.items():
            if field in extracted_data:
                continue  # Skip if already found
            
            for pattern in patterns:
                if pattern.lower() in line.lower():
                    # Found a potential field
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        value = parts[1].strip()
                        extracted_data[field] = value if value else "Not Found"
                        break
    
    # Set default values for any missing fields
    for field in field_patterns.keys():
        if field not in extracted_data:
            extracted_data[field] = "Not Found"
    
    return extracted_data
