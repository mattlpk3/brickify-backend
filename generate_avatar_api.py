from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

openai.api_key = os.environ.get("OPENAI_API_KEY")

# GPT-4o: Generate ultra-detailed visual prompt
def generate_structured_prompt(background, pose, phrase):
    system_instruction = (
        "You are generating a prompt for an official BRICKIFY avatar that follows an exact locked image format. "
        "Do not change the structure. The image must match previously confirmed outputs, including LEGO-style brick box, logo, icons, studs on top, and nameplate. "
        "Be extremely specific and force the visual format through strong phrasing. This prompt will be used for DALL·E 3."
    )

    user_input = f"""
Render a highly detailed 3D LEGO-style avatar of a real person based on the uploaded photo. The figure should have a LEGO-like head, body, and hands, with a strong resemblance to the real face. Pose the figure in a dynamic way: {pose}. 

The figure must be inside a red LEGO-style brick box on a transparent background.

The box must include:
- The word 'BRICKIFY' at the top in bold LEGO-style font.
- Underneath it: @, Instagram, TikTok, and X logos in this exact order — clean and small.
- Scene background: {background}.
- 3D LEGO brick studs on top.
- Bottom: a yellow LEGO nameplate that says: {phrase}.

The full box and avatar must resemble a professional LEGO toy render. Make the figure stylized and animated with sharp lighting.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_input}
        ]
    )

    return response["choices"][0]["message"]["content"]

# API Endpoint
@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get("photo")
        background = request.form.get("background")
        pose = request.form.get("pose")
        phrase = request.form.get("phrase")

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing fields"}), 400

        # Get locked prompt
        prompt = generate_structured_prompt(background, pose, phrase)

        # Generate image
        image_response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            response_format="url",
            quality="standard",
            n=1
        )

        image_url = image_response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


