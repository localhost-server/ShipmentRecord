# PDF Shipping Data Extractor

A Streamlit application that extracts shipping information from PDF courier airway bills using Anthropic AI (Claude) and exports the data to Excel.

## Features

- Upload PDF courier airway bills (single or batch processing)
- Extract key shipping information:
  - Order ID
  - Recipient Name
  - Recipient Address
  - Courier Name
  - Tracking Number
- Export data to Excel
- Support for multiple courier formats
- Real-time data preview
- Error handling and validation

## Requirements

- Python 3.8+
- Anthropic API key
- Required Python packages (installed via requirements.txt)

## Local Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.template` to `.env`
   - Add your API key in `.env`:
```bash
cp .env.template .env
```

4. Run the application:
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. Fork this repository to your GitHub account

2. Sign up for [Streamlit Community Cloud](https://streamlit.io/cloud)

3. Create a new app in Streamlit Cloud:
   - Click "New app"
   - Select your forked repository
   - Select the main branch
   - Set the Python file path to `app.py`

4. Set up environment secrets in Streamlit Cloud:
   - In your app's settings, find the "Secrets" section
   - Add your Anthropic API key:
```yaml
ANTHROPIC_API_KEY: "your-anthropic-api-key-here"
```

5. Deploy:
   - Streamlit Cloud will automatically deploy your app
   - Any commits pushed to your GitHub repository will trigger automatic redeployment

## File Structure
```
├── app.py                  # Main Streamlit application
├── requirements.txt        # Project dependencies
├── .env.template          # Template for environment variables
└── utils/
    ├── __init__.py
    ├── pdf_processor.py    # PDF text extraction
    ├── ai_extractor.py     # Anthropic AI integration
    └── excel_exporter.py   # Excel file creation
```

## Usage

1. Access your deployed app through Streamlit Cloud URL

2. Choose between:
   - Single PDF processing
   - Multiple PDF processing (batch mode)

3. Upload your PDF file(s)

4. Click "Process PDF" or "Process All PDFs"

5. Review the extracted information

6. Download the Excel file with the results

## Error Handling

The application includes comprehensive error handling for:
- PDF reading issues
- AI API connection problems
- Data extraction failures
- Excel file creation errors

Each error is logged and displayed to the user with helpful messages.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security Note

- Never commit your `.env` file or any files containing API keys
- Always use environment variables or secrets management for sensitive data
- The `.env.template` file is included as a reference but contains no real credentials
