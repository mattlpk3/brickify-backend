# BRICKIFY Avatar Generator Backend (Python Flask Example)
# This API endpoint handles file upload and user inputs, then calls an AI model to generate the LEGO-style avatar.

from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Replace with your Replicate API token or backend image generator
REPLICATE_API_TOKEN = "your_replicate_api_token"
REPLICATE_MODEL_URL = "https://api.replicate.com/v1/predictions"

@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    if 'photo' not in request.files:
        return jsonify({"error": "Missing image file"}), 400

    photo = request.files['photo']
    background = request.form.get('background', '')
    pose = request.form.get('pose', '')
    phrase = request.form.get('phrase', '')

    # Save uploaded photo temporarily
    file_path = os.path.join("uploads", photo.filename)
    photo.save(file_path)

    # Final locked BRICKIFY prompt
    prompt = f"""
Create a 3D LEGO-style avatar of the person in the uploaded image. The figure must closely resemble their face and wear appropriate LEGO-style features. Pose the figure in a dynamic way based on the input provided. Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. The top of the box must say 'BRICKIFY' in a bold LEGO-style font. Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}. The box must include 3D brick studs on top and feel like a real LEGO box. Style must remain consistent, professional, and unique to BRICKIFY.
"""

    # Send to Replicate (or custom model endpoint)
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "your_model_version_id",
        "input": {
            "prompt": prompt,
            "image": open(file_path, "rb")
        }
    }

    response = requests.post(REPLICATE_MODEL_URL, json=data, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to generate avatar"}), 500

    result = response.json()
    output_url = result.get("output", None)

    return jsonify({"avatar_url": output_url})

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True, port=5000)
