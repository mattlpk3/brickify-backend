import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def root():
    return jsonify({"status": "OK", "message": "BRICKIFY API is live"}), 200

@app.route("/api/generate-avatar", methods=["POST"])
def generate_avatar():
    try:
        # Get user data
        background = request.form.get("background")
        pose = request.form.get("pose")
        phrase = request.form.get("phrase")

        if "photo" not in request.files:
            return jsonify({"error": "No photo uploaded"}), 400

        photo = request.files["photo"]

        # Read image binary
        photo_bytes = photo.read()

        # Prompt for DALL·E
        prompt = f"LEGO-style 3D avatar box with background {background}, figure doing {pose}, name: {phrase}. Keep box design LEGO-style, branded with BRICKIFY, and show @ icons below the logo."

        # Generate image
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url

        return jsonify({
            "success": 1,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({
            "success": 0,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
