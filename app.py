from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import json
import os
import requests

app = Flask(__name__)

CORS(app, resources={r"/*": {
    "origins": "*", 
    "allow_headers": ["Content-Type", "Authorization"], 
    "methods": ["GET", "POST", "OPTIONS"]
}})

# API Key Render Environment Variables irraa dubbisa
gemini_key = os.environ.get("GEMINI_API_KEY", "")

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response

@app.route('/')
def home():
    return jsonify({"status": "healthy", "message": "Nile Job AI Backend is running perfectly!"})

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_assistant():
    if request.method == 'OPTIONS':
        return handle_options()
        
    try:
        if not request.is_json:
            return jsonify({"error": "JSON format required"}), 400
            
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "Message body is empty"}), 400

        system_instruction = (
            "You are the official Nile Job AI Assistant, an elite career coach and employment advisor. "
            "Help the user with any general questions, coding advice, video editing tips, or career guidance. "
            "Keep your responses professional, helpful, and highly motivational. Speak fluently in Afaan Oromoo, Amharic, or English based on the user's language."
        )

        # ── REST API CALL (Kallattiin Google Server waamuu - Bypass 404 SDK Errors) ──
        # Google Gemini 1.5 Flash Endpoint (Yeroo hunda kan hojjetu fi bilisa kan ta'e)
        url = f"https://googleapis.com{gemini_key}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_instruction}\n\nUser Question: {user_message}\nAI Response:"}
                    ]
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        # Deebii Google irraa dhufe kutaalee isaa qulqulleessanii baasuu
        if response.status_code == 200:
            try:
                ai_reply = response_data['candidates'][0]['content']['parts'][0]['text']
                return jsonify({"reply": ai_reply.strip()})
            except Exception:
                return jsonify({"reply": "Nile Job AI is processing your request. Please try again."})
        else:
            # Yoo 1.5 Flash dide, gara moodela dhaloota haaraatti fallback gochuu
            fallback_url = f"https://googleapis.com{gemini_key}"
            fb_response = requests.post(fallback_url, headers=headers, json=payload)
            fb_data = fb_response.json()
            if fb_response.status_code == 200:
                ai_reply = fb_data['candidates'][0]['content']['parts'][0]['text']
                return jsonify({"reply": ai_reply.strip()})
            else:
                return jsonify({"error": f"Google API Error: {fb_response.text}"}), fb_response.status_code
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
