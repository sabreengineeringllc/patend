import streamlit as st
import requests
import json
import os
from datetime import datetime

# Constants
USPTO_API_URL = "https://developer.uspto.gov/ibd-api/v1/patent/application"
USPTO_API_KEY = "1hqK2bo5.LS50G5gOKs9lqra4cGOb3sRwb3DDPklG"  # Replace with your USPTO API key

# Helper function to query USPTO API
def get_uspto_patents(query, max_results=10):
    """
    Fetches patent information from the USPTO API.
    :param query: Search query (e.g., "cordless vacuum cleaners")
    :param max_results: Maximum number of patents to retrieve
    :return: List of patents with headline information
    """
    # Construct the query parameters
    params = {
        "searchText": query,  # Search query
        "rows": max_results,  # Number of results to return
        "start": 0,  # Starting index of results
        "api_key": USPTO_API_KEY  # API key
    }
    try:
        response = requests.get(USPTO_API_URL, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        patents = data.get("response", {}).get("docs", [])
        return patents
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching USPTO patents: {e}")
        return []

# Helper function to download PDF files
def download_pdf(url, folder):
    """
    Downloads a PDF file from the given URL and saves it to the specified folder.
    :param url: URL of the PDF file
    :param folder: Folder to save the PDF file
    :return: Path to the downloaded PDF file
    """
    try:
        # Check if the URL points to a PDF file
        if not url.lower().endswith(".pdf"):
            print(f"Skipping non-PDF URL: {url}")
            return None

        # Send a HEAD request to check if the URL is reachable
        head_response = requests.head(url, allow_redirects=True)
        if head_response.status_code != 200:
            print(f"URL not reachable: {url} (Status Code: {head_response.status_code})")
            return None

        # Download the PDF file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        filename = os.path.basename(url)
        filepath = os.path.join(folder, filename)
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filepath
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None

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
            patents = get_uspto_patents(query, max_results=10)
            
            # Display results
            if patents:
                st.write(f"Found {len(patents)} patents:")
                for patent in patents:
                    st.write(f"**Patent ID:** {patent.get('patentNumber')}")
                    st.write(f"**Title:** {patent.get('patentTitle')}")
                    st.write(f"**Abstract:** {patent.get('abstractText')}")
                    st.write(f"**Inventors:** {', '.join(patent.get('inventors', []))}")
                    st.write(f"**Filing Date:** {patent.get('filingDate')}")
                    st.write("---")

                # Create a timestamped folder for PDF downloads
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_folder = f"patent_pdfs_{timestamp}"
                os.makedirs(download_folder, exist_ok=True)

                # Download PDFs for each patent
                downloaded_files = []
                for patent in patents:
                    if patent.get("pdfLink"):  # Check if a PDF link is available
                        pdf_url = patent["pdfLink"]
                        filepath = download_pdf(pdf_url, download_folder)
                        if filepath:
                            downloaded_files.append(filepath)
                            st.write(f"Downloaded PDF: {filepath}")

                st.write(f"Total PDFs downloaded: {len(downloaded_files)}")
            else:
                st.warning("No patents found.")
        else:
            st.error("Please enter an industry vertical or company name.")

# Run the Streamlit app
if __name__ == "__main__":
    main()