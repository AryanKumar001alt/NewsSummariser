from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import google.generativeai as genai

# Configure Gemini API Key
genai.configure(api_key="AIzaSyAscJFe-BQSUqfxr7ImMGk78LWsmxNNy3Q")

app = Flask(__name__, static_folder="frontend")
CORS(app)

# Fetch text from URL
def fetch_text_from_url(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        return text.strip() if text else None
    except Exception as e:
        print("Error fetching URL:", e)
        return None

# Simple bias detection
def detect_bias(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "Positive bias"
    elif polarity < -0.1:
        return "Negative bias"
    else:
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
        return jsonify({"error": f"Gemini API error: {str(e)}"}), 500

    bias = detect_bias(text)
    return jsonify({"summary": summary, "bias": bias})

# Serve frontend
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists("frontend/" + path):
        return send_from_directory("frontend", path)
    else:
        return send_from_directory("frontend", "index.html")

# Run backend
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
