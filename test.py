import requests
import os
from dotenv import load_dotenv

load_dotenv()

def check_with_safe_browsing_api(api_key, url):
    """Check the URL with Google Safe Browsing API."""
    safe_browsing_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    payload = {
        "client": {
            "clientId": "yourcompanyname",  # Replace with your company or project name
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    params = {"key": api_key}

    try:
        response = requests.post(safe_browsing_url, json=payload, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad HTTP status codes
        result = response.json()

        # Debugging information
        print(f"Safe Browsing API response: {result}")

        return "matches" in result  # Returns True if threats are found, False otherwise

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Handle specific HTTP errors
    except Exception as err:
        print(f"Other error occurred: {err}")  # Handle other possible errors

    return False  # Return False if the request fails

# Replace with your API key and test URL
api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
is_threat = check_with_safe_browsing_api(api_key, "https://www.youtube.com")
print("Is Threat:", is_threat)
