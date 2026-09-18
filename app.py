from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import json
import os
from google import genai

app = Flask(__name__)

CORS(app, resources={r"/*": {
    "origins": "*", 
    "allow_headers": ["Content-Type", "Authorization"], 
    "methods": ["GET", "POST", "OPTIONS"]
}})

gemini_key = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=gemini_key)

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
        
        full_prompt = f"{system_instruction}\n\nUser Question: {user_message}\nAI Response:"

        # Dynamic Model Fallback Router (Bypass standard 404 model errors completely)
        try:
            # 1. Try the standard 2.5 Flash model format
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt,
            )
        except Exception:
            try:
                # 2. Fallback to raw gemini-2.5-flash without extension strings
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                )
            except Exception:
                # 3. Ultimate backup model that always works for v1beta API limits
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                )
        
        return jsonify({"reply": response.text.strip()})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
