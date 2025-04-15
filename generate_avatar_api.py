from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])


# ✅ Set your OpenAI key (in production, use environment variables)
openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-..."

# ✅ Step 1: Generate the BRICKIFY prompt using GPT-4o
def generate_brickify_prompt(description, background, pose, name):
    system_prompt = (
        "You are a prompt generator that formats user photo descriptions into a locked LEGO-style BRICKIFY avatar prompt. "
        "Do not change the format or style."
    )

    user_prompt = f"""
Create a 3D LEGO-style avatar of the person in the uploaded image. The figure must closely resemble their face and wear appropriate LEGO-style features. Pose the figure in a dynamic way based on the input provided. Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. The top of the box must say 'BRICKIFY' in a bold LEGO-style font. Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {name}. The box must include 3D brick studs on top and feel like a real LEGO box and around it should be transparent background if possible. Style must remain consistent, professional, and unique to BRICKIFY.

Background: {background}
Pose or Accessory: {pose}
Name or Phrase: {name}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return response['choices'][0]['message']['content']

# ✅ Step 2: Generate the image with DALL·E 3
def generate_brickify_image(prompt):
    response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        response_format="url",
        quality="standard",
        n=1
    )
    return response['data'][0]['url']

# ✅ Avatar generation endpoint
@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        # Get data from form
        photo = request.files.get('photo')  # We do not use it in prompt
        background = request.form.get('background')
        pose = request.form.get('pose')
        name = request.form.get('phrase')

        if not all([background, pose, name]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        # 💡 Optional: provide a short manual description of the uploaded photo
        # (because OpenAI API here does not handle image input)
        description = "Image of a person to convert into a LEGO-style avatar"

        # Generate prompt using GPT-4o
        final_prompt = generate_brickify_prompt(description, background, pose, name)

        # Generate image using DALL·E 3
        image_url = generate_brickify_image(final_prompt)

        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

# ✅ Run Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
