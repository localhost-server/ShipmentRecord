import pandas as pd
import io
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_excel_file(df):
    """
    Create an Excel file from a pandas DataFrame containing shipping data.
    
    Args:
        df (pd.DataFrame): DataFrame with extracted shipping information
        
    Returns:
        bytes: Excel file as bytes for download
    """
    logger.info("Creating Excel file from extracted data")
    
    try:
        # Create a buffer to hold the Excel file
        buffer = io.BytesIO()
        
        # Create Excel writer using the buffer
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Write the DataFrame to the Excel file
            df.to_excel(writer, sheet_name='Shipping Data', index=False)
            
            # Access the workbook and the worksheet
            workbook = writer.book
            worksheet = writer.sheets['Shipping Data']
            
            # Format the columns for better readability
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                # Find the maximum length in the column
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Set the column width based on the maximum length (with some padding)
                adjusted_width = max_length + 2
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Set the buffer position to the beginning
        buffer.seek(0)
        
        # Get the bytes from the buffer
        excel_data = buffer.getvalue()
        
        logger.info("Excel file created successfully")
        return excel_data
    
    except Exception as e:
        logger.error(f"Error creating Excel file: {str(e)}")
        raise Exception(f"Failed to create Excel file: {str(e)}")

def generate_filename():
    """
    Generate a filename for the Excel file with a timestamp.
    
    Returns:
        str: Filename with timestamp
    """
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate filename
    filename = f"shipping_data_{timestamp}.xlsx"
    
    return filename

def create_multiple_records_excel(data_list):
    """
    Create an Excel file from multiple shipping records.
    
    Args:
        data_list (list): List of dictionaries containing shipping data
        
    Returns:
        bytes: Excel file as bytes for download
    """
    # Convert list of records to DataFrame
    df = pd.DataFrame(data_list)
    
    # Create Excel file
    return create_excel_file(df)
