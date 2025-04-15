from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

openai.api_key = os.getenv("OPENAI_API_KEY")


# 🧠 Step 1: Let GPT-4o generate the final structured BRICKIFY prompt
def generate_structured_prompt(background, pose, phrase):
    system_instruction = (
        "You are generating a prompt for an official BRICKIFY avatar that follows an exact locked image format. "
        "Do not change the structure. The image must match previously confirmed outputs, including LEGO-style brick box, logo, icons, studs on top, and nameplate. "
        "Be extremely specific and force the visual format through strong phrasing. This prompt will be used for DALL·E 3."
    )

    user_input = f"""
Render a highly detailed 3D LEGO-style avatar of a real person based on the uploaded photo. 
The figure should have a LEGO-like head, body, and hands, with a strong resemblance to the real face. 
The figure must be inside a red LEGO-style brick box that includes the word 'BRICKIFY' at the top in a bold LEGO font, 
followed by these icons: @, Instagram, TikTok, and X (Twitter) — small and clean. 
The background must be a {background} scene. Pose the figure in a dynamic way matching: {pose}. 
There must be 3D brick studs on top of the box and a yellow LEGO-style nameplate at the bottom that says: {phrase}. 
The entire box and figure must appear on a transparent background, and look like an authentic LEGO product shot.
"""

    chat_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_input}
        ]
    )
    return chat_response.choices[0].message.content


# 🎯 Avatar Generation Endpoint
@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields."})

        # Generate detailed prompt using GPT-4o
        refined_prompt = generate_structured_prompt(background, pose, phrase)

        # Generate image with DALL·E 3
        image_response = openai.images.generate(
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)


