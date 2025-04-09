import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from werkzeug.utils import secure_filename
import tempfile


# Initialize OpenAI with GPT-4o support
client = OpenAI()

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])  # <-- 🔥 VERY IMPORTANT

@app.route("/api/generate-avatar", methods=["POST"])
def generate_avatar():
    if 'photo' not in request.files:
        return jsonify({"success": 0, "message": "Missing photo"}), 400

    photo = request.files['photo']
    background = request.form.get("background", "")
    pose = request.form.get("pose", "")
    phrase = request.form.get("phrase", "")

    if not all([background, pose, phrase]):
        return jsonify({"success": 0, "message": "Missing required fields"}), 400

    # Save uploaded image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp:
        photo.save(temp.name)
        image_path = temp.name

    try:
        # Locked BRICKIFY prompt
        prompt = f"""
        Create a 3D LEGO-style avatar of the person in the uploaded image. The figure must closely resemble their face and wear appropriate LEGO-style features. Pose the figure in a dynamic way based on the input provided. Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. The top of the box must say 'BRICKIFY' in a bold LEGO-style font. Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}. The box must include 3D brick studs on top and feel like a real LEGO box and around it should be transparent background if possible. Style must remain consistent, professional, and unique to BRICKIFY.

        Background: {background}
        Pose or Accessory: {pose}
        Name or Phrase: {phrase}
        """

        # Generate image with GPT-4o + DALL-E 3
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1,
            response_format="url",
            image=open(image_path, "rb")
        )

        image_url = response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
