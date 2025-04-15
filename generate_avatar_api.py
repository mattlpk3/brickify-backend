from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

openai.api_key = os.environ.get("OPENAI_API_KEY")

# 🧠 Step 1: Enhanced GPT-4o Prompt Generator
def generate_structured_prompt(background, pose, phrase):
    system_instruction = (
        "You are generating a prompt for an official BRICKIFY avatar that follows an exact locked image format. "
        "Do not change the structure. The image must match previously confirmed outputs, including LEGO-style brick box, logo, icons, studs on top, and nameplate. "
        "Be extremely specific and force the visual format through strong phrasing. This prompt will be used for DALL·E 3."
    )

    user_input = f"""
Render a highly detailed 3D LEGO-style avatar of a real person based on the uploaded photo. The figure should have a LEGO-like head, body, and hands, with a strong resemblance to the real face. Pose the figure in a dynamic way based on this input: {pose}. 

The figure must be placed inside a red LEGO-style brick box with a transparent background. 

The box must include:
- The word 'BRICKIFY' at the top in a bold LEGO-style font.
- Directly underneath: these small and clean icons in this exact order — @, Instagram logo, TikTok logo, and X (Twitter) logo.
- The background scene must be: {background}.
- 3D LEGO brick studs must be on top of the box.
- At the bottom, show a yellow LEGO-style nameplate with the name or phrase: {phrase}.
- The entire box must feel like an official LEGO product with clear lighting, clean render, and transparency around the object.

Never change this structure.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_input}
        ]
    )

    return response['choices'][0]['message']['content']

@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        # Step 1: Generate full detailed prompt
        final_prompt = generate_structured_prompt(background, pose, phrase)

        # Step 2: Generate image from prompt
        image_response = openai.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            size="1024x1024",
            response_format="url",
            quality="standard",
            n=1
        )

        image_url = image_response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)

