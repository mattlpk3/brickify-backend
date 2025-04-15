from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

# 🔐 Init Flask app + CORS
app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

# 🔑 OpenAI client setup
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 🎯 Generate structured BRICKIFY prompt using GPT-4o
def generate_structured_prompt(background, pose, phrase):
    system_instruction = (
        "You are generating a prompt for an official BRICKIFY avatar that follows an exact locked image format. "
        "Do not change the structure. The image must match previously confirmed outputs, including LEGO-style brick box, logo, icons, studs on top, and nameplate. "
        "Be extremely specific and force the visual format through strong phrasing. This prompt will be used for DALL·E 3."
    )

    user_input = f"""
Create a 3D LEGO-style avatar of the person in the uploaded image. The figure must closely resemble their face and wear appropriate LEGO-style features. Pose the figure in a dynamic way based on the input provided. Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. The top of the box must say 'BRICKIFY' in a bold LEGO-style font. Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}. The box must include 3D brick studs on top and feel like a real LEGO box and around brick should be transparent background every time.

Background: {background}
Pose or Accessory: {pose}
Name or Phrase: {phrase}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

# 📸 Endpoint for BRICKIFY generation
@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        prompt = generate_structured_prompt(background, pose, phrase)

        image = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            response_format="url",
            n=1
        )

        return jsonify({"success": 1, "image_url": image.data[0].url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

# 🔁 Run server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)

