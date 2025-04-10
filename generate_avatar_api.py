from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

# ✅ Initialize OpenAI client using new SDK format
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY") or "sk-...")

# ✅ Generate locked BRICKIFY prompt
def generate_prompt(background, pose, phrase):
    return f"""
    Create a 3D LEGO-style avatar of the person in the uploaded image.
    The figure must closely resemble their face and wear appropriate LEGO-style features.
    Pose the figure in a dynamic way based on the input provided.

    Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene.
    The top of the box must say 'BRICKIFY' in a bold LEGO-style font.
    Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean.
    At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}.
    The box must include 3D brick studs on top and feel like a real LEGO box and around it should be transparent background if possible.
    Style must remain consistent, professional, and unique to BRICKIFY.

    Pose or Accessory: {pose}
    Background: {background}
    Name or Phrase: {phrase}
    """

# ✅ API endpoint for generating avatars
@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        # Generate the official BRICKIFY prompt
        prompt = generate_prompt(background, pose, phrase)

        # Use GPT-4o (via DALL·E 3) to generate the image
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="url",
            style="vivid"
        )

        image_url = response.data[0].url

        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
