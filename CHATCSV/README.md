# CSV Chat Assistant

A Streamlit application that allows users to upload CSV files and interact with their data using natural language. Powered by Anthropic's Claude 3 Opus and Streamlit.

## Features

- Upload any CSV file for analysis
- Ask questions about your data in natural language
- Generate visualizations automatically
- Get statistical insights and analysis
- Interactive charts and tables

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Set up your Anthropic API key:
   - Get an API key from [Anthropic](https://console.anthropic.com/)
   - Copy the `.env.example` file to `.env`
   - Replace the placeholder with your actual Anthropic API key

## Usage

1. Run the application:

```bash
streamlit run interface.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)
3. Upload a CSV file
4. Ask questions about your data
5. View the results including visualizations

## Example Questions

- What is the average salary for each department?
- Can you create a bar chart showing the number of employees by department?
- Who has the highest salary?
- What's the correlation between years of experience and salary?
- Create a line chart of salary vs years of experience

## How It Works

The application uses Claude 3 Opus language model to analyze your CSV data and respond to natural language queries. The model:

1. Analyzes the structure of your uploaded CSV
2. Processes your questions in context of the data
3. Generates appropriate responses, including visualizations when relevant
4. Returns results in a structured format that can be displayed in the Streamlit interface

## Dependencies

- `streamlit`: Web application framework
- `pandas`: Data manipulation library
- `anthropic`: Anthropic API client library
- `plotly`: Interactive visualizations
- `matplotlib`: Visualization backend
- `numpy`: Numerical operations
- `python-dotenv`: Environment variable management

## Customization

You can modify the system prompt in the `agent.py` file to customize how the AI responds to queries. The visualization components in `interface.py` can also be extended to support more chart types.
