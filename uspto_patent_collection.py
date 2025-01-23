import streamlit as st
import requests
import json
from datetime import datetime

# Constants
USPTO_API_URL = "https://api.patentsview.org/patents/query"

# Helper function to query USPTO API
def get_uspto_patents(query, max_results=100):
    """
    Fetches headline patent information from the USPTO API using PatentsView.
    :param query: Search query (e.g., "cordless vacuum cleaners")
    :param max_results: Maximum number of patents to retrieve
    :return: List of patents with headline information
    """
    # Construct the query parameters
    params = {
        "q": json.dumps({"_text_any": {"patent_title": query}}),  # Search in patent titles
        "f": json.dumps(["patent_id", "patent_title", "patent_abstract", "inventors", "assignees", "patent_date"]),
        "o": json.dumps({"per_page": max_results})
    }
    try:
        response = requests.get(USPTO_API_URL, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        patents = data.get("patents", [])
        return patents
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching USPTO patents: {e}")
        return []

# Streamlit UI
def main():
    st.title("USPTO Patent Collection Tool")
    st.write("Enter the industry vertical and company name to collect patents from the USPTO.")

    # Input fields
    industry_vertical = st.text_input("Industry Vertical (e.g., cordless vacuum cleaners):")
    company_name = st.text_input("Company Name (e.g., Dyson):")

    # Combine inputs into a query
    query = f"{industry_vertical} {company_name}".strip()

    # Button to trigger patent collection
    if st.button("Collect Patents"):
        if query:
            st.write(f"Collecting patents for: {query}")
            patents = get_uspto_patents(query, max_results=50)
            
            # Display results
            if patents:
                st.write(f"Found {len(patents)} patents:")
                for patent in patents:
                    st.write(f"**Patent ID:** {patent.get('patent_id')}")
                    st.write(f"**Title:** {patent.get('patent_title')}")
                    st.write(f"**Abstract:** {patent.get('patent_abstract')}")
                    st.write(f"**Inventors:** {', '.join([inv['inventor_name'] for inv in patent.get('inventors', [])])}")
                    st.write(f"**Filing Date:** {patent.get('patent_date')}")
                    st.write("---")
            else:
                st.warning("No patents found.")
        else:
            st.error("Please enter an industry vertical or company name.")

# Run the Streamlit app
if __name__ == "__main__":
    main()