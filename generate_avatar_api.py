from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

# ✅ Flask Setup
app = Flask(__name__)
CORS(app)

# ✅ Environment Key (will fail loud if missing)
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("Missing OPENAI_API_KEY")

# ✅ Prompt Generator
def generate_prompt(background, pose, phrase):
    return (
        f"Create a LEGO-style minifigure avatar inside a BRICKIFY plastic toy box. "
        f"The background is {background}, the pose or accessory is {pose}, "
        f"and the name at the bottom says '{phrase}'. The box includes the BRICKIFY logo "
        f"and LEGO-style icons for Instagram, TikTok, and X."
    )

# ✅ Route Handler
@app.route("/api/generate-avatar", methods=["POST"])
def generate_avatar():
    try:
        # ✅ Get Fields
        photo = request.files.get("photo")
        background = request.form.get("background")
        pose = request.form.get("pose")
        phrase = request.form.get("phrase")

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"}), 400

        # ✅ Generate Prompt
        prompt = generate_prompt(background, pose, phrase)

        # ✅ Generate Image
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1
        )

        image_url = response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500

# ✅ Start Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

