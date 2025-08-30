from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import google.generativeai as genai

# Configure Gemini API key (set as environment variable)
genai.configure(api_key=os.environ.get("GENAI_API_KEY"))

# Set static folder to frontend
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
    if polarity > 0.1: return "Positive bias"
    if polarity < -0.1: return "Negative bias"
    return "Neutral"

# API endpoint
@app.route("/analyze", methods=["POST"])
def analyze_news():
    data = request.json
    url = data.get("url")
    text = data.get("text")
    tone = data.get("tone", "neutral")

    if url and not text:
        text = fetch_text_from_url(url)
        if not text:
            return jsonify({"error": "Failed to fetch article from URL"}), 400

    if not text:
        return jsonify({"error": "No text or URL provided"}), 400

    try:
        prompt = f"Summarize the following article in a {tone} tone:\n\n{text}"
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        print("Gemini API error:", e)
        summary = "Summary unavailable: Could not reach Gemini API."

    return jsonify({"summary": summary, "bias": detect_bias(text)})

# Serve frontend files
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
