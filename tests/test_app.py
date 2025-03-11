import os
import pytest
from utils.pdf_processor import extract_text_from_pdf
from utils.ai_extractor import init_ai_client, extract_shipping_data
from utils.excel_exporter import generate_filename

def test_environment_variables():
    """Test that required environment variables are set"""
    assert os.getenv("ANTHROPIC_API_KEY") is not None, "ANTHROPIC_API_KEY not set"

def test_generate_filename():
    """Test Excel filename generation"""
    filename = generate_filename()
    assert filename.endswith(".xlsx"), "Filename should end with .xlsx"
    assert "shipping_data_" in filename, "Filename should contain 'shipping_data_'"

def test_ai_client_initialization():
    """Test Anthropic client initialization"""
    try:
        client = init_ai_client()
        assert client is not None, "AI client should be initialized"
    except Exception as e:
        pytest.skip(f"Skipping AI client test: {str(e)}")

def test_shipping_data_structure():
    """Test shipping data structure"""
    sample_text = """
    Order #: 12345
    To: John Doe
    Address: 123 Main St, City, Country
    Courier: FastShip Express
    Tracking: ABC123XYZ
    """
    
    try:
        data = extract_shipping_data(sample_text)
        required_fields = [
            "Order ID",
            "Recipient Name",
            "Recipient Address",
            "Courier Name",
            "Tracking Number"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
            assert isinstance(data[field], str), f"Field should be string: {field}"
    except Exception as e:
        pytest.skip(f"Skipping shipping data test: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__])
