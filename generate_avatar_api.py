from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

# ✅ Initialize OpenAI client with v1.x SDK
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 🔁 Step 1: Generate locked BRICKIFY prompt using GPT-4o
def generate_structured_prompt(background, pose, phrase):
    system_instruction = "You are a prompt generator that outputs a perfectly formatted BRICKIFY prompt. Do not change structure."

    user_input = f"""
Create a 3D LEGO-style avatar of the person in the uploaded image. The figure must closely resemble their face and wear appropriate LEGO-style features. Pose the figure in a dynamic way based on the input provided. Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. The top of the box must say 'BRICKIFY' in a bold LEGO-style font. Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}. The box must include 3D brick studs on top and feel like a real LEGO box and around brick should be transparent background everytime.

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

# 🧱 Step 2: Endpoint to generate avatar
@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        # 🔁 Use GPT-4o to format the prompt
        refined_prompt = generate_structured_prompt(background, pose, phrase)

        # 🎨 Send prompt to DALL·E 3 for image generation
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=refined_prompt,
            size="1024x1024",
            quality="standard",
            response_format="url",
            n=1
        )

        image_url = image_response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

# 🚀 Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
