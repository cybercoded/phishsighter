from flask import Flask, request, jsonify, render_template
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

@app.route("/")
def index():
    return render_template('index.html')  # Make sure you have an 'index.html' in your templates folder

@app.route("/check_url", methods=["POST"])
def check_url():
    try:
        data = request.get_json()
        url = data.get("url", "").strip()
        logger.info(f"Received URL: {url}")

        if not url:
            return jsonify({"error": "No URL provided."}), 400

        # Step 1: Check URL safety using Google Safe Browsing API
        api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
        if not api_key:
            logger.error("Google Safe Browsing API key is missing!")
            return jsonify({"error": "API key not configured."}), 500

        is_threat = check_with_safe_browsing_api(api_key, url)

        if is_threat:
            return jsonify({"is_phishing": True, "message": "The URL is flagged as dangerous by Google Safe Browsing."})

        # Step 2: Check URL reachability
        reachable, final_url = is_url_reachable(url)
        if not reachable:
            return jsonify({"error": "The URL is not reachable."}), 400

        # Step 3: Proceed with feature extraction and prediction
        try:
            obj = FeatureExtraction(final_url)
            features = obj.getFeaturesList()
        except Exception as e:
            logger.error(f"Error during feature extraction for {final_url}: {e}")
            return jsonify({"error": "Feature extraction failed."}), 500

        try:
            x = np.array(features).reshape(1, -1)
            y_pred = gbc.predict(x)[0]
            y_pro_phishing = gbc.predict_proba(x)[0, 0]
            y_pro_non_phishing = gbc.predict_proba(x)[0, 1]

            if y_pred == 1:
                return jsonify({
                    "is_phishing": False,
                    "message": f"The site is {y_pro_non_phishing * 100:.2f}% safe.",
                    "y_pro_phishing": y_pro_phishing,
                    "features": features,
                    "y_pro_non_phishing": y_pro_non_phishing
                })
            else:
                return jsonify({
                    "is_phishing": True,
                    "message": f"The site is {y_pro_phishing * 100:.2f}% likely to be a phishing site.",
                    "y_pro_phishing": y_pro_phishing,
                    "features": features,
                    "y_pro_non_phishing": y_pro_non_phishing
                })
        except Exception as e:
            logger.error(f"Error during model prediction for {final_url}: {e}")
            return jsonify({"error": "Prediction failed."}), 500

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == "__main__":
    app.run(debug=True)
