from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

# Set OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt enhancer: Strong instruction for GPT-4o to follow locked BRICKIFY format
def generate_structured_prompt(background, pose, phrase):
    system_instruction = (
        "You are generating a prompt for an official BRICKIFY avatar that follows an exact locked image format. "
        "Do not change the structure. The image must match previously confirmed outputs, including LEGO-style brick box, "
        "logo, icons, studs on top, and nameplate. Be extremely specific and force the visual format through strong phrasing."
    )

    user_input = f"""
Render a highly detailed 3D LEGO-style avatar of a real person based on the uploaded photo. 
The figure should have a LEGO-like head, body, and hands, with a strong resemblance to the real face. 
Pose the figure in a dynamic way based on the input provided. 
The figure must be inside a red LEGO-style brick box that includes the word 'BRICKIFY' at the top in a bold LEGO font, 
followed by these icons in this exact order: @, Instagram, TikTok, and X (Twitter). 
The background must be a {background} scene. 
There must be 3D brick studs on top of the box and a yellow LEGO-style nameplate at the bottom that says: {phrase}. 
The entire box and figure must appear on a transparent background, and look like an authentic LEGO product shot.

Pose: {pose}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_input}
        ]
    )

    return response.choices[0].message.content

# Main avatar generation endpoint
@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        prompt = generate_structured_prompt(background, pose, phrase)

        # Generate image with DALL-E 3
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
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




