from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# 🧠 Step 1: Let GPT-4o generate the final structured prompt
def generate_structured_prompt(background, pose, phrase):
    system_instruction = "You are a prompt generator that outputs a perfectly formatted BRICKIFY prompt. Do not change structure."

    user_input = f"""
Create a 3D LEGO-style avatar of the person in the uploaded image. The figure must closely resemble their face and wear appropriate LEGO-style features. Pose the figure in a dynamic way based on the input provided. Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. The top of the box must say 'BRICKIFY' in a bold LEGO-style font. Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}. The box must include 3D brick studs on top and feel like a real LEGO box and around brick should be transparent background everytime.

Background: {background}
Pose or Accessory: {pose}
Name or Phrase: {phrase}
"""

    gpt_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_input}
        ]
    )
    return gpt_response['choices'][0]['message']['content']


@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        # 🧠 Get final DALL·E prompt from GPT-4o
        refined_prompt = generate_structured_prompt(background, pose, phrase)

        # 🎨 Now generate the image with DALL·E 3 using refined prompt
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
