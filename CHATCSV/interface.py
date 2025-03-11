import streamlit as st
import pandas as pd
import json
import tempfile
import os
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from agent import create_agent, query_agent

def decode_response(response: str) -> dict:
    """
    Convert the string response from the model to a dictionary object.
    
    Args:
        response (str): Response from the model
        
    Returns:
        dict: Dictionary with response data
    """
    try:
        # Try to parse directly as JSON
        return json.loads(response)
    except json.JSONDecodeError:
        # If direct loading fails, show error
        st.error("Failed to parse response from AI. Please try a different query.")
        return {"answer": "I couldn't parse the response. Please try a different query."}

def write_response(response_dict: dict):
    """
    Write a response from an agent to a Streamlit app.
    
    Args:
        response_dict (dict): The response from the agent
        
    Returns:
        None
    """
    # Check if the response is an answer
    if "answer" in response_dict:
        # Display just the answer text, not the raw JSON
        st.markdown(response_dict["answer"])
    
    # Check if the response is a table
    if "table" in response_dict:
        try:
            data = response_dict["table"]
            
            # Convert all data to strings to avoid type conversion issues
            safe_data = []
            for row in data["data"]:
                safe_row = [str(item) if isinstance(item, (list, dict)) else item for item in row]
                safe_data.append(safe_row)
                
            df = pd.DataFrame(safe_data, columns=data["columns"])
            
            st.subheader("Data Table")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error displaying table: {str(e)}")
            st.write("Raw table data:")
            st.write(data)
    
    # Check if the response is a bar chart
    if "bar" in response_dict:
        try:
            data = response_dict["bar"]
            
            # Convert all data to proper types for plotting
            # Numbers should be numbers, text should be strings
            processed_data = []
            for row in data["data"]:
                # Ensure second value is numeric
                if len(row) >= 2:
                    try:
                        # Convert second item to float if possible
                        processed_row = [row[0], float(row[1])]
                        processed_data.append(processed_row)
                    except (ValueError, TypeError):
                        # Skip rows with non-numeric second values
                        st.warning(f"Skipping row with non-numeric value: {row}")
                else:
                    processed_data.append(row)
            
            if processed_data:
                df = pd.DataFrame(processed_data, columns=data["columns"])
                
                st.subheader("Bar Chart")
                
                # Use plotly for interactive charts
                fig = px.bar(
                    df, 
                    x=df.columns[0], 
                    y=df.columns[1],
                    title=f"{df.columns[1]} by {df.columns[0]}",
                    labels={
                        df.columns[0]: df.columns[0],
                        df.columns[1]: df.columns[1]
                    }
                )
                st.plotly_chart(fig)
            else:
                st.error("Could not create bar chart: no valid data")
        except Exception as e:
            st.error(f"Error displaying bar chart: {str(e)}")
            st.write("Raw chart data:")
            st.write(data)
    
    # Check if the response is a line chart
    if "line" in response_dict:
        try:
            data = response_dict["line"]
            
            # Convert all data to proper types for plotting
            processed_data = []
            for row in data["data"]:
                if len(row) >= 2:
                    try:
                        # Try to convert second item to float if possible
                        processed_row = [row[0], float(row[1])]
                        processed_data.append(processed_row)
                    except (ValueError, TypeError):
                        st.warning(f"Skipping row with non-numeric value: {row}")
                else:
                    processed_data.append(row)
            
            if processed_data:
                df = pd.DataFrame(processed_data, columns=data["columns"])
                
                st.subheader("Line Chart")
                
                # Use plotly for interactive charts
                fig = px.line(
                    df, 
                    x=df.columns[0], 
                    y=df.columns[1],
                    title=f"{df.columns[1]} over {df.columns[0]}",
                    labels={
                        df.columns[0]: df.columns[0],
                        df.columns[1]: df.columns[1]
                    }
                )
                st.plotly_chart(fig)
            else:
                st.error("Could not create line chart: no valid data")
        except Exception as e:
            st.error(f"Error displaying line chart: {str(e)}")
            st.write("Raw chart data:")
            st.write(data)
            
    # Check if the response is a pie chart
    if "pie" in response_dict:
        try:
            data = response_dict["pie"]
            
            # Ensure labels and values are provided
            if "labels" in data and "values" in data:
                # Ensure all values are numeric
                processed_values = []
                processed_labels = []
                
                for i, (label, value) in enumerate(zip(data["labels"], data["values"])):
                    try:
                        # Convert value to float
                        processed_values.append(float(value))
                        processed_labels.append(str(label))
                    except (ValueError, TypeError):
                        st.warning(f"Skipping pie slice with non-numeric value: {label}: {value}")
                
                if processed_values and processed_labels:
                    st.subheader("Pie Chart")
                    
                    # Use plotly for interactive pie chart
                    fig = go.Figure(data=[go.Pie(
                        labels=processed_labels,
                        values=processed_values,
                        hole=0.3,  # Creates a donut chart effect
                        textinfo='label+percent',
                        insidetextorientation='radial'
                    )])
                    
                    # Update layout
                    fig.update_layout(
                        title="Distribution by Category",
                        height=500,
                        margin=dict(t=60, b=0, l=0, r=0)
                    )
                    
                    st.plotly_chart(fig)
                else:
                    st.error("Could not create pie chart: no valid data")
            else:
                st.error("Pie chart data missing labels or values")
                
        except Exception as e:
            st.error(f"Error displaying pie chart: {str(e)}")
            st.write("Raw pie chart data:")
            st.write(data)

def main():
    st.set_page_config(
        page_title="CSV Chat Assistant", 
        page_icon="📊", 
        layout="wide"
    )
    
    st.title("📊 CSV Chat Assistant")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv", 
        help="Upload a CSV file to analyze"
    )
    
    if uploaded_file is not None:
        try:
            # Load the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Sample Data Preview
            st.subheader("Sample Data")
            st.dataframe(df.head(5))
            
            # Create a container for the chat interface
            chat_container = st.container()
            
            with chat_container:
                # Query input
                query = st.text_input(
                    "Ask a question about your data", 
                    placeholder="What insights can you provide?"
                )
                
                # Submit button
                if st.button("Analyze", type="primary"):
                    if query:
                        with st.spinner("Analyzing your data..."):
                            try:
                                # Create a temporary file
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                                    df.to_csv(tmp_file.name, index=False)
                                    tmp_file_path = tmp_file.name
                                
                                # Create an agent from the CSV file
                                agent = create_agent(tmp_file_path)
                                
                                # Query the agent
                                response = query_agent(agent=agent, query=query)
                                
                                # Decode the response
                                decoded_response = decode_response(response)
                                
                                # Create a result container
                                result_container = st.container()
                                
                                with result_container:
                                    st.subheader("Results")
                                    # Write the response to the Streamlit app
                                    write_response(decoded_response)
                                
                                # Clean up the temporary file
                                os.unlink(tmp_file_path)
                            
                            except Exception as e:
                                st.error(f"An error occurred: {str(e)}")
                    else:
                        st.warning("Please enter a query.")
        
        except Exception as e:
            st.error(f"Error loading CSV file: {str(e)}")

if __name__ == "__main__":
    main()
