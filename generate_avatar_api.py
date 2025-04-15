import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Step 1: Generate strong BRICKIFY prompt via GPT-4o
def generate_brickify_prompt(background, pose, phrase):
    system_msg = (
        "You are generating a prompt for an official BRICKIFY avatar that follows an exact locked image format. "
        "The image must replicate the previously confirmed layout exactly: 3D LEGO figure, red LEGO-style box, BRICKIFY logo, "
        "icons (@, Instagram, TikTok, X), yellow nameplate at the bottom, transparent background, brick studs on top. "
        "Force DALL·E 3 to follow this layout using very strong visual phrasing."
    )

    user_input = f"""
Render a highly detailed 3D LEGO-style avatar of a real person based on the uploaded photo. The figure should have a LEGO-like head, body, and hands, with a strong resemblance to the real face. The figure must be inside a red LEGO-style brick box that includes the word 'BRICKIFY' at the top in a bold LEGO font, followed by these icons: @, Instagram, TikTok, and X (Twitter). The background must be a {background} scene. There must be 3D brick studs on top of the box and a yellow LEGO-style nameplate at the bottom that says: {phrase}. The entire box and figure must appear on a transparent background, and look like an authentic LEGO product shot.

Background: {background}
Pose or Accessory: {pose}
Name or Phrase: {phrase}
"""

    chat = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_input}
        ]
    )
    return chat.choices[0].message.content

@app.route("/api/generate-avatar", methods=["POST"])
def generate_avatar():
    try:
        photo = request.files.get("photo")
        background = request.form.get("background")
        pose = request.form.get("pose")
        phrase = request.form.get("phrase")

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"}), 400

        # Generate the BRICKIFY image prompt
        prompt = generate_brickify_prompt(background, pose, phrase)

        # Generate image via DALL·E 3
        image_resp = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            response_format="url"
        )

        image_url = image_resp.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


