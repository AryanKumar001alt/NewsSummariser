from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import google.generativeai as genai

# Configure Gemini API key from environment variable
genai.configure(api_key=os.environ.get("GENAI_API_KEY"))

# Create Flask app and set frontend folder
app = Flask(__name__, static_folder="frontend")
CORS(app)

# Fetch text from URL
def fetch_text_from_url(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = soup.find_all("p")
        return " ".join([p.get_text() for p in paragraphs]).strip()
    except Exception as e:
        print("Error fetching URL:", e)
        return None

# Simple bias detection
def detect_bias(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive bias"
    elif polarity < -0.1:
        return "Negative bias"
    return "Neutral"

# API endpoint
@app.route("/analyze", methods=["POST"])
def analyze_news():
    try:
        data = request.json
        url = data.get("url")
        text = data.get("text")
        tone = data.get("tone", "neutral")

        if url and not text:
            text = fetch_text_from_url(url)
            if not text:
                return jsonify({"summary": "", "bias": "", "error": "Failed to fetch article from URL"}), 400

        if not text:
            return jsonify({"summary": "", "bias": "", "error": "No text or URL provided"}), 400

        try:
            prompt = f"Summarize the following article in a {tone} tone:\n\n{text}"
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            summary = response.text
        except Exception as e:
            print("Gemini API error:", e)
            summary = "Summary unavailable"
        
        bias = detect_bias(text)
        return jsonify({"summary": summary, "bias": bias, "error": ""})
    
    except Exception as e:
        print("Unexpected server error:", e)
        return jsonify({"summary": "", "bias": "", "error": "Server error occurred"}), 500

# Serve frontend files
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    # Fallback to index.html
    index_file = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index_file):
        return send_from_directory(app.static_folder, "index.html")
    return "Frontend not found", 404


# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
