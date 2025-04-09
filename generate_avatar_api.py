# ✅ Updated Flask backend to lock and apply the final BRICKIFY prompt structure

from flask import Flask
from flask_cors import CORS
import openai
import os


app = Flask(__name__)

# Allow only your frontend
CORS(app, resources={r"/api/*": {"origins": "https://trenchmoney.online"}})


openai.api_key = os.getenv("OPENAI_API_KEY")

# Locked prompt template
LOCKED_PROMPT_TEMPLATE = (
    "Create a 3D LEGO-style avatar of the person in the uploaded image. "
    "The figure must closely resemble their face and wear appropriate LEGO-style features. "
    "Pose the figure in a dynamic way based on the input provided. "
    "Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. "
    "The top of the box must say 'BRICKIFY' in a bold LEGO-style font. "
    "Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. "
    "At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}. "
    "The box must include 3D brick studs on top and feel like a real LEGO box and around it should be transparent background if possible. "
    "Style must remain consistent, professional, and unique to BRICKIFY."
)

@app.route("/api/generate-avatar", methods=["POST"])
def generate_avatar():
    if 'photo' not in request.files:
        return jsonify({"success": 0, "message": "Missing image"}), 400

    photo = request.files['photo']
    background = request.form.get("background")
    pose = request.form.get("pose")
    phrase = request.form.get("phrase")

    if not all([photo, background, pose, phrase]):
        return jsonify({"success": 0, "message": "Missing required fields"}), 400

    # Construct the final prompt using the locked format
    final_prompt = LOCKED_PROMPT_TEMPLATE.format(
        background=background,
        phrase=phrase
    ) + f"\n\nPose or Accessory: {pose}"

    try:
        # Call OpenAI Image API
        response = openai.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="url"
        )

        image_url = response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
