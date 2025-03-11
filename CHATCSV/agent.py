import pandas as pd
import numpy as np
import json
import os
import re
from dotenv import load_dotenv
from anthropic import Anthropic

class AIAgent:
    def __init__(self, df):
        """
        Initialize the AI Agent with a dataframe.
        
        Args:
            df (pandas.DataFrame): The dataframe to analyze
        """
        self.df = df
        load_dotenv()
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"  # Using Claude 3 Opus
        
        # Analyze dataframe structure
        self._analyze_dataframe()
    
    def _analyze_dataframe(self):
        """Analyze the dataframe structure to provide context to the model."""
        self.columns = self.df.columns.tolist()
        self.dtypes = {col: str(dtype) for col, dtype in zip(self.columns, self.df.dtypes)}
        self.sample_data = self.df.head(3).to_string(index=False)
        self.shape = self.df.shape
        
        # Generate basic statistics for numerical columns
        self.numeric_stats = {}
        for col in self.df.select_dtypes(include=[np.number]).columns:
            self.numeric_stats[col] = {
                'min': float(self.df[col].min()),
                'max': float(self.df[col].max()),
                'mean': float(self.df[col].mean()),
                'median': float(self.df[col].median())
            }
    
    def _get_dataframe_context(self):
        """Create a context string with information about the dataframe."""
        context = f"CSV Data Information:\n"
        context += f"- Shape: {self.shape[0]} rows, {self.shape[1]} columns\n"
        context += f"- Columns: {', '.join(self.columns)}\n"
        context += f"- Data Types: {json.dumps(self.dtypes)}\n"
        
        if self.numeric_stats:
            context += f"- Numeric Statistics: {json.dumps(self.numeric_stats)}\n"
        
        context += f"\nSample Data:\n{self.sample_data}\n"
        return context
    
    def _extract_json_from_text(self, text):
        """
        Attempt to extract a valid JSON object from text that might have extra content.
        
        Args:
            text (str): Text that may contain a JSON object
            
        Returns:
            str: Valid JSON string or None if extraction fails
        """
        # Try to find JSON between curly braces
        matches = re.findall(r'\{.*\}', text, re.DOTALL)
        
        if matches:
            for match in matches:
                try:
                    # Test if this is valid JSON
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue
        
        # Try standard method to extract from markdown code blocks
        if "```json" in text:
            parts = text.split("```json")
            if len(parts) > 1:
                json_candidate = parts[1].split("```")[0].strip()
                try:
                    json.loads(json_candidate)
                    return json_candidate
                except json.JSONDecodeError:
                    pass
        
        if "```" in text:
            parts = text.split("```")
            if len(parts) > 1:
                json_candidate = parts[1].strip()
                try:
                    json.loads(json_candidate)
                    return json_candidate
                except json.JSONDecodeError:
                    pass
        
        return None
    
    def _generate_bar_data(self, columns):
        """Generate data for a bar chart."""
        if len(columns) == 1:
            # Count frequency of values in the column
            value_counts = self.df[columns[0]].value_counts().reset_index()
            return {
                "columns": ["category", "count"],
                "data": value_counts.values.tolist()
            }
        elif len(columns) == 2:
            # Group by first column and aggregate second column (mean)
            agg_data = self.df.groupby(columns[0])[columns[1]].mean().reset_index()
            return {
                "columns": columns,
                "data": agg_data.values.tolist()
            }
        return {"error": "Invalid number of columns for bar chart"}
    
    def _generate_line_data(self, columns):
        """Generate data for a line chart."""
        if len(columns) == 2:
            # Sort by the first column (typically a date or sequence)
            sorted_data = self.df.sort_values(columns[0])
            
            return {
                "columns": columns,
                "data": sorted_data[columns].values.tolist()
            }
        return {"error": "Line charts require exactly two columns"}
    
    def _generate_pie_data(self, column, value_column=None):
        """
        Generate data for a pie chart.
        
        Args:
            column (str): The column to use for category labels
            value_column (str, optional): The column to use for values. If None, counts are used.
        
        Returns:
            dict: Pie chart data with labels and values
        """
        if value_column:
            # Group by the category column and sum the value column
            grouped = self.df.groupby(column)[value_column].sum().reset_index()
            return {
                "labels": grouped[column].tolist(),
                "values": grouped[value_column].tolist()
            }
        else:
            # Count frequency of values in the column
            value_counts = self.df[column].value_counts()
            return {
                "labels": value_counts.index.tolist(),
                "values": value_counts.values.tolist()
            }
    
    def should_include_visualization(self, query):
        """
        Determine if visualization should be included based on user query.
        
        Args:
            query (str): The user's query
            
        Returns:
            bool: True if visualization should be included, False otherwise
        """
        visualization_keywords = [
            'chart', 'plot', 'graph', 'visualize', 'visualization', 'visual', 
            'show me', 'display', 'pie chart', 'bar chart', 'line chart',
            'histogram', 'scatter plot', 'distribution'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in visualization_keywords)
    
    def answer_query(self, query):
        """
        Send a query to the Anthropic API and get a response.
        
        Args:
            query (str): The query to send to the API
            
        Returns:
            str: JSON formatted response with answer and/or visualization data
        """
        # Check if visualization should be included
        include_visualization = self.should_include_visualization(query)
        
        # Get dataframe context
        df_context = self._get_dataframe_context()
        
        # Prepare system message with context and instructions
        system_message = f"""You are an AI assistant specialized in analyzing CSV data and providing insights.
You have access to a CSV file with the following information:

{df_context}

IMPORTANT: Your response must be in valid JSON format only, with no text before or after.
Do not include markdown code blocks, explanations, or anything outside the JSON object.

Format your responses as JSON with the "answer" field always included:
- "answer": string with your text response

IMPORTANT ABOUT VISUALIZATIONS:
Only include visualization data if the user explicitly requests it by mentioning words like "chart", "plot", 
"graph", "visualize", "show me", etc. Do not include visualization data otherwise.

If visualization is requested, you may include any of these additional fields:
- "table": dict with "columns" and "data" for tabular data
- "bar": dict with "columns" and "data" for bar charts 
- "line": dict with "columns" and "data" for line charts
- "pie": dict with "labels" and "values" for pie charts

For pie charts, provide:
- "labels": array of category names (strings)
- "values": array of corresponding numeric values

If you include a table, bar chart, line chart, or pie chart:
1. All values must be either numbers or strings, no mixed types
2. For percentages, use the numeric value (e.g., 0.68 instead of "68%")
3. Don't include complex string representations like "Male: 68%, Female: 32%" in data intended for charts
4. Ensure all data is properly formatted for visualization

Example response format WITH visualization (only if the user explicitly requests it):
{{
  "answer": "Based on the data, the average salary is $77,100.",
  "table": {{
    "columns": ["Department", "Average Salary"],
    "data": [["Engineering", 77500], ["Marketing", 88333], ["Sales", 65333]]
  }},
  "bar": {{
    "columns": ["Department", "Average Salary"],
    "data": [["Engineering", 77500], ["Marketing", 88333], ["Sales", 65333]]
  }}
}}

Example response format WITHOUT visualization (for most queries):
{{
  "answer": "Based on the data, the average salary is $77,100. Engineering has an average of $77,500, Marketing averages $88,333, and Sales averages $65,333."
}}

Remember: Return ONLY a valid JSON object. No text before or after. No markdown formatting.
"""
        
        # Prepare user message with the query
        user_message = query
        if include_visualization:
            user_message += " Include relevant visualizations in your response."
        
        # Send request to Anthropic API
        try:
            message = self.client.messages.create(
                model=self.model,
                system=system_message,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=4096,
                temperature=0
            )
            
            raw_response = message.content[0].text
            
            # First, try to parse directly as JSON
            try:
                json_obj = json.loads(raw_response)
                return json.dumps(json_obj)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                extracted_json = self._extract_json_from_text(raw_response)
                if extracted_json:
                    # Validate extracted JSON
                    try:
                        json_obj = json.loads(extracted_json)
                        return json.dumps(json_obj)
                    except json.JSONDecodeError:
                        pass
                
                # If all attempts fail, create a simple answer with the text
                # Use regex to clean up the response to just plain text
                cleaned_text = re.sub(r'```.*?```', '', raw_response, flags=re.DOTALL)  # Remove code blocks
                cleaned_text = re.sub(r'[`*_#]', '', cleaned_text)  # Remove markdown formatting
                cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)  # Remove extra newlines
                cleaned_text = cleaned_text.strip()
                
                # Create a simple answer object
                answer = {
                    "answer": cleaned_text
                }
                return json.dumps(answer)
                
        except Exception as e:
            error_response = {
                "answer": f"Error: {str(e)}. Please try a different query or check your API key."
            }
            return json.dumps(error_response)
        
    def analyze_data(self, analysis_type, column=None):
        """
        Perform data analysis on the dataframe.
        
        Args:
            analysis_type (str): Type of analysis to perform
            column (str, optional): Column to analyze
            
        Returns:
            dict: Analysis results
        """
        if analysis_type == "summary":
            return {
                "columns": self.columns,
                "shape": self.shape,
                "dtypes": self.dtypes
            }
        
        elif analysis_type == "statistics" and column:
            if column not in self.columns:
                return {"error": f"Column '{column}' not found"}
            
            if pd.api.types.is_numeric_dtype(self.df[column]):
                return {
                    "min": float(self.df[column].min()),
                    "max": float(self.df[column].max()),
                    "mean": float(self.df[column].mean()),
                    "median": float(self.df[column].median()),
                    "std": float(self.df[column].std())
                }
            else:
                # For non-numeric columns
                return {
                    "unique_values": self.df[column].nunique(),
                    "most_common": self.df[column].value_counts().nlargest(5).to_dict()
                }
        
        elif analysis_type == "correlation":
            if not self.df.select_dtypes(include=[np.number]).columns.tolist():
                return {"error": "No numeric columns available for correlation analysis"}
            
            corr = self.df.select_dtypes(include=[np.number]).corr().round(2)
            return {"correlation_matrix": corr.to_dict()}
        
        return {"error": "Invalid analysis type or missing parameters"}


def create_agent(csv_file_path):
    """
    Create an AI agent from a CSV file.
    
    Args:
        csv_file_path (str): Path to the CSV file
    
    Returns:
        AIAgent: An AI agent loaded with the CSV data
    """
    # Load CSV data
    df = pd.read_csv(csv_file_path)
    
    # Create agent
    agent = AIAgent(df)
    
    return agent


def query_agent(agent, query):
    """
    Query an AI agent.
    
    Args:
        agent (AIAgent): The agent to query
        query (str): The query to send to the agent
    
    Returns:
        str: The response from the agent
    """
    return agent.answer_query(query)
