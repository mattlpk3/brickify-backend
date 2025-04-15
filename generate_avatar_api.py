from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

# 🔒 Locked BRICKIFY Prompt Instruction
def generate_brickify_prompt(background, pose, phrase):
    system_instruction = (
        "You are generating a prompt for an official BRICKIFY avatar that follows an exact locked image format. "
        "Do not change the structure. The image must match previously confirmed outputs, including LEGO-style brick box, logo, icons, studs on top, and nameplate. "
        "Be extremely specific and force the visual format through strong phrasing. This prompt will be used for DALL·E 3."
    )

        user_input = f"""
Render a 3D LEGO-style avatar of a real person based on their face. The figure must have a yellow LEGO-style head, hands, and body with strong facial resemblance to the person.

Pose the figure in a dynamic LEGO-style position based on this input: {pose}.

Place the figure inside a bold red LEGO-style brick box that looks like an official LEGO product box. The box must be fully 3D, include realistic LEGO-style brick studs on the top, and appear slightly angled to show depth.

On the top front of the box, show the word "BRICKIFY" in large bold LEGO-style yellow text.

Directly underneath that, display these icons in this exact order — small, centered, and spaced evenly: @ symbol, Instagram logo, TikTok logo, and X (Twitter) logo.

The internal background scene inside the box must be: {background}.

At the bottom of the box, include a yellow LEGO-style nameplate that says: {phrase}, using a bold font that matches the LEGO aesthetic.

Surrounding the entire brick box and figure, make sure there is a fully transparent background — do not include shadows or external scenery. The box must float cleanly on a transparent canvas.

The image must resemble a high-quality LEGO product render with accurate depth, lighting, and 3D form.

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

# 🚀 API Endpoint
@app.route("/api/generate-avatar", methods=["POST"])
def generate_avatar():
    try:
        background = request.form.get("background")
        pose = request.form.get("pose")
        phrase = request.form.get("phrase")

        if not all([background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"}), 400

        # Generate locked prompt from GPT-4o
        prompt = generate_brickify_prompt(background, pose, phrase)

        # Generate image with DALL·E 3
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            response_format="url"
        )

        image_url = image_response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


