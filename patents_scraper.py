import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import requests
from datetime import datetime

# Helper function to scrape Google Patents using Selenium
def scrape_google_patents(query, max_results=10):
    """
    Scrapes patent information from Google Patents using Selenium.
    :param query: Search query (e.g., "cordless vacuum cleaners Dyson")
    :param max_results: Maximum number of patents to retrieve
    :return: List of patents with headline information
    """
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Navigate to Google Patents
        driver.get("https://patents.google.com/")
        time.sleep(2)  # Wait for the page to load

        # Enter the search query
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for the search results to load

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract patent data
        patents = []
        for result in soup.select("div.search-result-item"):  # Updated CSS selector
            title = result.select_one("h3").text.strip() if result.select_one("h3") else "N/A"
            link = result.select_one("a")["href"] if result.select_one("a") else "N/A"
            abstract = result.select_one("div.abstract").text.strip() if result.select_one("div.abstract") else "N/A"
            inventors = result.select_one("div.inventors").text.strip() if result.select_one("div.inventors") else "N/A"
            filing_date = result.select_one("div.filing-date").text.strip() if result.select_one("div.filing-date") else "N/A"

            patents.append({
                "title": title,
                "link": link,
                "abstract": abstract,
                "inventors": inventors,
                "filing_date": filing_date
            })

        return patents[:max_results]  # Limit the number of results
    except Exception as e:
        st.error(f"Error scraping Google Patents: {e}")
        return []
    finally:
        driver.quit()  # Close the browser

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
    st.title("Patents Scraper to collect public training data for ai innovations")
    st.write("Enter the industry vertical and company name to collect patents from Google Patents.")

    # Input fields
    industry_vertical = st.text_input("Industry Vertical (e.g., cordless vacuum cleaners):")
    company_name = st.text_input("Company Name (e.g., Dyson):")

    # Combine inputs into a query
    query = f"{industry_vertical} {company_name}".strip()

    # Button to trigger patent collection
    if st.button("Collect Patents"):
        if query:
            st.write(f"Collecting patents for: {query}")
            patents = scrape_google_patents(query, max_results=10)
            
            # Display results
            if patents:
                st.write(f"Found {len(patents)} patents:")
                for patent in patents:
                    st.write(f"**Title:** {patent.get('title')}")
                    st.write(f"**Link:** {patent.get('link')}")
                    st.write(f"**Abstract:** {patent.get('abstract')}")
                    st.write(f"**Inventors:** {patent.get('inventors')}")
                    st.write(f"**Filing Date:** {patent.get('filing_date')}")
                    st.write("---")

                # Create a timestamped folder for PDF downloads
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_folder = f"patent_pdfs_{timestamp}"
                os.makedirs(download_folder, exist_ok=True)

                # Remove duplicate links
                unique_links = set()
                for patent in patents:
                    if patent["link"] != "N/A":
                        unique_links.add(patent["link"])

                # Download PDFs for each unique link
                downloaded_files = []
                for link in unique_links:
                    filepath = download_pdf(link, download_folder)
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