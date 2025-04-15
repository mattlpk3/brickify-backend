from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])


# 🔐 Secure your API key here
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-..."

# ✅ Step 1: BRICKIFY locked prompt builder using GPT-4o
def build_locked_prompt(background, pose, phrase):
    system_msg = "You are a creative assistant for a LEGO-style avatar generator called BRICKIFY."
    user_msg = f"""
Create a 3D LEGO-style avatar of the person in the uploaded image. The figure must closely resemble their face and wear appropriate LEGO-style features. Pose the figure in a dynamic way based on the input provided. Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. The top of the box must say 'BRICKIFY' in a bold LEGO-style font. Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}. The box must include 3D brick studs on top and feel like a real LEGO box. Style must remain consistent, professional, and unique to BRICKIFY and around brick should be transparent background everytime. The LEGO figure must match the photo and include this pose or accessory: {pose}.
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    )

    return response.choices[0].message.content.strip()


# ✅ Step 2: Send locked prompt to DALL·E 3 and return image URL
def generate_dalle_image(prompt):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="url"
    )
    return response.data[0].url


# ✅ Step 3: API endpoint
@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        # 🔒 Use GPT-4o to build prompt based on locked format
        prompt = build_locked_prompt(background, pose, phrase)

        # 🎨 Generate image from DALL·E 3 using that prompt
        image_url = generate_dalle_image(prompt)

        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
