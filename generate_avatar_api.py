from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

def generate_brickify_prompt(background, pose, phrase):
    system_instruction = (
        "You are generating a prompt for an official BRICKIFY avatar that follows an exact locked image format. "
        "Do not change the structure. The image must match previously confirmed outputs, including LEGO-style brick box, logo, icons, studs on top, and nameplate. "
        "Be extremely specific and force the visual format through strong phrasing. This prompt will be used for DALL·E 3."
    )

    user_input = f"""
Create a 3D LEGO-style avatar of the person in the uploaded image. The figure must closely resemble their face and wear appropriate LEGO-style features. 
Pose the figure in a dynamic way based on the input provided. 
Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. 
The top of the box must say 'BRICKIFY' in a bold LEGO-style font. 
Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. 
At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}. 
The box must include 3D brick studs on top and feel like a real LEGO box. Style must remain consistent, professional, and unique to BRICKIFY and around brick should be transparent background everytime.

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

    return response.choices[0].message.content.strip()

@app.route("/api/generate-avatar", methods=["POST"])
def generate_avatar():
    try:
        background = request.form.get("background")
        pose = request.form.get("pose")
        phrase = request.form.get("phrase")

        if not all([background, pose, phrase]):
            return jsonify({"success": 0, "message": f"Missing fields - BG: {background}, Pose: {pose}, Phrase: {phrase}"}), 400

        prompt = generate_brickify_prompt(background, pose, phrase)

        image_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1080x1350",
            quality="standard",
            response_format="url"
        )

        image_url = image_response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
