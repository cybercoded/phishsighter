from flask import Flask, request, render_template
import numpy as np
import warnings
import pickle
import requests
from feature import FeatureExtraction
from dotenv import load_dotenv
import os
import logging

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.template_filter('zip')
def zip_filter(a, b):
    return zip(a, b)

app.jinja_env.filters['zip'] = zip_filter

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
        # Handle API failures by assuming no threat
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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        logger.info(f"Received URL: {url}")

        if not url:
            pred = "No URL provided. Please enter a valid URL."
            return render_template('index.html', prediction=pred, features=[], url=url, y_pro_phishing=0, y_pro_non_phishing=0)

        # Step 1: Check URL safety using Google Safe Browsing API
        api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
        if not api_key:
            logger.error("Google Safe Browsing API key is missing!")
            pred = "Internal error: API key not configured. Please try again later."
            return render_template('index.html', prediction=pred, features=[], url=url, y_pro_phishing=0, y_pro_non_phishing=0)

        is_threat = check_with_safe_browsing_api(api_key, url)

        if is_threat:
            pred = "The URL is flagged as dangerous by Google Safe Browsing. Please avoid visiting this site."
            return render_template('index.html', prediction=pred, features=[], url=url, y_pro_phishing=0, y_pro_non_phishing=0)

        # Step 2: Check URL reachability
        reachable, final_url = is_url_reachable(url)
        if not reachable:
            pred = "The URL is not reachable. Please check the URL and try again."
            return render_template('index.html', prediction=pred, features=[], url=url, y_pro_phishing=0, y_pro_non_phishing=0)

        # Step 3: Proceed with feature extraction and prediction
        try:
            obj = FeatureExtraction(final_url)
            features = obj.getFeaturesList()
        except Exception as e:
            logger.error(f"Error during feature extraction for {final_url}: {e}")
            pred = "An error occurred while extracting features from the URL. Please try again later."
            return render_template('index.html', prediction=pred, features=[], url=final_url, y_pro_phishing=0, y_pro_non_phishing=0)

        try:
            x = np.array(features).reshape(1, -1)
            y_pred = gbc.predict(x)[0]
            y_pro_phishing = gbc.predict_proba(x)[0, 0]
            y_pro_non_phishing = gbc.predict_proba(x)[0, 1]

            if y_pred == 1:
                pred = f"is {y_pro_non_phishing * 100:.2f}% safe to go."
            else:
                pred = f"is {y_pro_phishing * 100:.2f}% likely to be a phishing site."
        except Exception as e:
            logger.error(f"Error during model prediction for {final_url}: {e}")
            pred = "An error occurred while predicting the URL safety. Please try again later."
            y_pro_phishing = 0
            y_pro_non_phishing = 0

        return render_template(
            'index.html', 
            prediction=pred, 
            features=features, 
            url=final_url, 
            y_pro_phishing=y_pro_phishing, 
            y_pro_non_phishing=y_pro_non_phishing
        )

    # GET request handling
    return render_template("index.html", prediction="", features=[], url="", y_pro_phishing=0, y_pro_non_phishing=0)

if __name__ == "__main__":
    app.run(debug=True)
