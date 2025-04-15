import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])  # ✅ This was missing

openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_brickify_prompt(background, pose, name):
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

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content.strip()

def generate_brickify_image(prompt):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        response_format="url",
        quality="standard",
        n=1
    )
    return response.data[0].url

@app.route("/api/generate-avatar", methods=["POST"])
def generate_avatar():
    try:
        image = request.files.get("image")
        background = request.form.get("background")
        pose = request.form.get("pose")
        name = request.form.get("name")

        if not all([image, background, pose, name]):
            return jsonify({"error": "Missing one or more fields"}), 400

        # Step 1: Generate prompt using GPT-4o
        prompt = generate_brickify_prompt(background, pose, name)

        # Step 2: Generate image from prompt using DALL·E 3
        image_url = generate_brickify_image(prompt)

        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
