from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from flask import Flask, request, jsonify
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

# 🔐 OpenAI API Key
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-...your-real-api-key..."

# 🧠 Generate image prompt
def generate_prompt(background, pose, phrase):
    return f"""
    Create a LEGO-style minifigure avatar inside a realistic plastic BRICKIFY toy box.
    The background should be {background}. Pose or accessory: {pose}.
    Text at the bottom: "{phrase}".
    The top of the box must include the BRICKIFY logo and icons for Instagram, TikTok, and X.
    Make sure the avatar resembles the user's uploaded photo.
    """

@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"}), 400

        # Temporarily save image in /tmp (Render's allowed space)
        temp_path = f"/tmp/{photo.filename}"
        photo.save(temp_path)

        prompt = generate_prompt(background, pose, phrase)

        # 🧠 Generate image via DALL·E 3 using OpenAI >= 1.0.0
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        image_url = response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
