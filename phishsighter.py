from flask import Flask, request, jsonify, render_template
import numpy as np
import warnings
import pickle
import requests
from urllib.parse import urlparse
from feature import FeatureExtraction
from dotenv import load_dotenv
import os
import logging
from flask_cors import CORS
import argparse
from tqdm import tqdm
import time  # For simulating the progress bar updates

warnings.filterwarnings('ignore')

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler for logging
log_file = "error_logs.log"
file_handler = logging.FileHandler(log_file)

# Create a formatter and set it for the file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Ensure no logging goes to the console (remove other handlers)
logger.propagate = False

# Load environment variables from .env file
load_dotenv()

# Load the pre-trained model
try:
    with open("models/ensemble_model.pkl", "rb") as file:
        gbc = pickle.load(file)
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading the model: {e}")
    gbc = None

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes and all origins
CORS(app)

def check_with_safe_browsing_api(api_key, url):
    """Check the URL with Google Safe Browsing API."""
    safe_browsing_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    payload = {
        "client": {
            "clientId": "yourcompanyname",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE", 
                "SOCIAL_ENGINEERING", 
                "UNWANTED_SOFTWARE", 
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    params = {"key": api_key}
    try:
        response = requests.post(safe_browsing_url, json=payload, params=params, timeout=5)
        response.raise_for_status()
        result = response.json()
        is_threat = "matches" in result and bool(result["matches"])
        logger.info(f"Safe Browsing API response for {url}: {result}")
        return is_threat
    except requests.RequestException as e:
        logger.error(f"Safe Browsing API request failed for {url}: {e}")
        return False

def is_url_reachable(url):
    """Check if the URL is reachable, trying https first if the url starts with http."""
    try:
        if url.startswith("http://"):
            https_url = url.replace("http://", "https://", 1)
            logger.info(f"Trying HTTPS URL: {https_url}")
            response = requests.head(https_url, allow_redirects=True, timeout=5)
            if response.status_code == 200:
                logger.info(f"HTTPS URL is reachable: {https_url}")
                return True, https_url
        logger.info(f"Trying original URL: {url}")
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            logger.info(f"Original URL is reachable: {url}")
            return True, url
    except requests.RequestException as e:
        logger.error(f"Error checking URL reachability for {url}: {e}")
    return False, None

def download_phishing_page(url):
    """Download the HTML content of the phishing page and append the URL to a file if it doesn't already exist."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Extract the domain name from the URL
            domain_name = urlparse(url).netloc
            
            # Define the file path using only the domain name
            os.makedirs("phishing_pages", exist_ok=True)  # Ensure directory exists
            file_path = os.path.join("phishing_pages", f"{domain_name}.html")
            
            # Write the HTML content to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            
            logger.info(f"Downloaded and saved phishing page: {file_path}")
            
            # Check if the URL already exists in phishing-site-urls.txt
            urls_file = "phishing-site-urls.txt"
            if os.path.exists(urls_file):
                with open(urls_file, 'r', encoding='utf-8') as url_file:
                    existing_urls = url_file.read().splitlines()
            else:
                existing_urls = []

            # Append the URL if it's not already present
            if url not in existing_urls:
                with open(urls_file, 'a', encoding='utf-8') as url_file:
                    url_file.write(f"{url}\n")
                logger.info(f"Appended URL to phishing-site-urls.txt: {url}")
            else:
                logger.info(f"URL already exists in phishing-site-urls.txt: {url}")
        
        else:
            logger.error(f"Failed to download the phishing page, status code: {response.status_code}")
    
    except requests.RequestException as e:
        logger.error(f"Error downloading phishing page for {url}: {e}")

def process_url(url, show_progress=False):
    """Process a URL from the terminal using the check_url logic, return message and features."""
    logger.info(f"Received URL: {url}")

    # Initialize progress bar for CLI mode
    if show_progress:
        tqdm_bar = tqdm(total=5, desc="Processing URL", unit="step")

    # Step 1: Check URL safety using Google Safe Browsing API
    if show_progress:
        tqdm_bar.update(1)  # Progress step 1: Starting the process

    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
    if not api_key:
        logger.error("Google Safe Browsing API key is missing!")
        if show_progress:
            tqdm_bar.close()
        return "Error: API key not configured.", []

    if show_progress:
        tqdm_bar.update(1)  # Progress step 2: Checking Safe Browsing API

    is_threat = check_with_safe_browsing_api(api_key, url)

    if is_threat:
        if show_progress:
            tqdm_bar.update(1)  # Progress step 3: URL is a phishing site
        download_phishing_page(url)
        if show_progress:
            tqdm_bar.close()
        return f"'{url}' is 100% a phishing URL", []

    # Step 2: Check URL reachability
    if show_progress:
        tqdm_bar.update(1)  # Progress step 4: Checking URL reachability

    reachable, final_url = is_url_reachable(url)
    if not reachable:
        if show_progress:
            tqdm_bar.close()
        return f"is not reachable", []

    # Step 3: Proceed with feature extraction and prediction
    try:
        obj = FeatureExtraction(final_url)
        features = obj.getFeaturesList()
    except Exception as e:
        logger.error(f"Error during feature extraction for {final_url}: {e}")
        if show_progress:
            tqdm_bar.close()
        return "Error: Feature extraction failed.", []

    if show_progress:
        tqdm_bar.update(1)  # Progress step 5: Extracting features

    try:
        x = np.array(features).reshape(1, -1)
        y_pred = gbc.predict(x)[0]
        y_pro_phishing = gbc.predict_proba(x)[0, 0]
        y_pro_non_phishing = gbc.predict_proba(x)[0, 1]

        if y_pred == 1:
            if show_progress:
                tqdm_bar.close()
            return f"is {y_pro_non_phishing * 100:.2f}% safe.", features
        else:
            download_phishing_page(final_url)
            if show_progress:
                tqdm_bar.close()
            return f"is {y_pro_phishing * 100:.2f}% likely to be a phishing site.", features
    except Exception as e:
        logger.error(f"Error during model prediction for {final_url}: {e}")
        if show_progress:
            tqdm_bar.close()
        return "Error: Prediction failed.", []



@app.route("/")
def index():
    return render_template('index.html')  # Make sure you have an 'index.html' in your templates folder

@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.get_json()
    url = data.get("url", "").strip()
    message, features = process_url(url)
    return jsonify({"message": message, "features": features})

if __name__ == "__main__":
    # Set up argparse for command-line arguments
    parser = argparse.ArgumentParser(description="Phishing detection app with Flask and URL handling.")
    parser.add_argument("-u", "--url", help="URL of the phishing site to analyze")
    parser.add_argument("--debug", action="store_true", help="Run Flask in debug mode.")
    args = parser.parse_args()

    if args.url:
        # If a URL is provided via the command line, process it
        message, features = process_url(args.url, show_progress=True)
        print(f"Message: {args.url} {message}")
        # print(f"Features: {features}")
    else:
        # If no URL is provided, run the Flask app
        app.run(debug=args.debug)
