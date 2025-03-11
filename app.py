import streamlit as st
import pandas as pd
import tempfile
import os
from dotenv import load_dotenv

# Import our utility modules
from utils.pdf_processor import extract_text_from_pdf
from utils.ai_extractor import extract_shipping_data
from utils.excel_exporter import create_excel_file, create_multiple_records_excel, generate_filename

# Load environment variables
load_dotenv()

# Set up page configuration
st.set_page_config(
    page_title="Shipping Data Extractor",
    page_icon="📦",
    layout="wide"
)

# Sidebar with about info
with st.sidebar:
    st.title("About")
    st.info(
        "This application extracts shipping information from PDF courier "
        "airway bills using Anthropic AI and exports the data to Excel. "
        "You can process single or multiple PDF files."
    )

# Main content
st.title("📦 Shipping Data Extractor")
st.markdown("""
Extract shipping information from courier airway bills (PDFs) and export to Excel.
The following fields will be extracted:
- Order ID
- Recipient Name
- Recipient Address
- Courier Name
- Tracking Number
""")

# File upload section
upload_option = st.radio("Choose upload option:", ["Single PDF", "Multiple PDFs"])

if upload_option == "Single PDF":
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'])
    
    if uploaded_file:
        process_button = st.button("Process PDF")
        if process_button:
            with st.spinner("Processing PDF... This may take a moment."):
                try:
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        pdf_path = tmp_file.name
                    
                    # Process PDF
                    pdf_text = extract_text_from_pdf(pdf_path)
                    extracted_data = extract_shipping_data(pdf_text)
                    
                    # Display results
                    st.subheader("Extracted Shipping Data")
                    df = pd.DataFrame([extracted_data])
                    st.dataframe(df)
                    
                    # Create and offer Excel download
                    excel_file = create_excel_file(df)
                    st.download_button(
                        label="Download Excel File",
                        data=excel_file,
                        file_name=generate_filename(),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                
                finally:
                    # Cleanup
                    if 'pdf_path' in locals() and os.path.exists(pdf_path):
                        os.unlink(pdf_path)

else:  # Multiple PDFs
    uploaded_files = st.file_uploader("Upload PDF files", type=['pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        process_button = st.button("Process All PDFs")
        if process_button:
            with st.spinner("Processing PDFs... This may take a moment."):
                all_extracted_data = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        # Update progress
                        progress = (i + 1) / len(uploaded_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing file {i + 1} of {len(uploaded_files)}: {uploaded_file.name}")
                        
                        # Create temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            pdf_path = tmp_file.name
                        
                        # Process PDF
                        pdf_text = extract_text_from_pdf(pdf_path)
                        extracted_data = extract_shipping_data(pdf_text)
                        extracted_data['File Name'] = uploaded_file.name
                        all_extracted_data.append(extracted_data)
                        
                        # Cleanup
                        os.unlink(pdf_path)
                    
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                
                # Display results
                if all_extracted_data:
                    st.subheader("Extracted Shipping Data")
                    df = pd.DataFrame(all_extracted_data)
                    st.dataframe(df)
                    
                    # Create and offer Excel download
                    excel_file = create_multiple_records_excel(all_extracted_data)
                    st.download_button(
                        label="Download Excel File",
                        data=excel_file,
                        file_name=generate_filename(),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                progress_bar.empty()
                status_text.empty()
