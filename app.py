# Importing required libraries
from flask import Flask, request, render_template, url_for, redirect
import numpy as np
import warnings
import pickle
from feature import FeatureExtraction

warnings.filterwarnings('ignore')

# Load the pre-trained model
file = open("models/ensemble_model.pkl", "rb")
gbc = pickle.load(file)
file.close()

# Initialize Flask app
app = Flask(__name__)

@app.template_filter('zip')
def zip_filter(a, b):
    return zip(a, b)

app.jinja_env.filters['zip'] = zip_filter

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        obj = FeatureExtraction(url)
        features = obj.getFeaturesList()
        print(features)  # Debug print statement
        x = np.array(features).reshape(1, -1) 

        y_pred = gbc.predict(x)[0]
        y_pro_phishing = gbc.predict_proba(x)[0, 0]
        y_pro_non_phishing = gbc.predict_proba(x)[0, 1]

        pred = "It is {0:.2f}% safe to go ".format(y_pro_non_phishing * 100) if y_pred == 1 else "It is {0:.2f}% likely to be a phishing site".format(y_pro_phishing * 100)
        
        return render_template('index.html', prediction=pred, features=features, url=url, y_pro_phishing=y_pro_phishing, y_pro_non_phishing=y_pro_non_phishing)
    
    return render_template("index.html", prediction="", features=[], url="", y_pro_phishing=0, y_pro_non_phishing=0)

if __name__ == "__main__":
    app.run(debug=True)