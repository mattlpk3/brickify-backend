from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# ✅ Set OpenAI API Key
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-..."

# ✅ Generate the official locked BRICKIFY prompt using GPT-4o
def generate_locked_prompt(user_description, background, pose, phrase):
    prompt_base = f"""
    Create a 3D LEGO-style avatar of the person in the uploaded image. The figure must closely resemble their face and wear appropriate LEGO-style features. Pose the figure in a dynamic way based on the input provided. Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. The top of the box must say 'BRICKIFY' in a bold LEGO-style font. Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}. The box must include 3D brick studs on top and feel like a real LEGO box and around it should be transparent background if possible. Style must remain consistent, professional, and unique to BRICKIFY.

    Background: {background}
    Pose or Accessory: {pose}
    Name or Phrase: {phrase}
    """
    return prompt_base.strip()

# ✅ Main API endpoint
@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        # Get user inputs
        photo = request.files.get('photo')  # not currently used in prompt
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields."})

        # 👇 Use GPT-4o if you want to generate prompt dynamically — here we use fixed version
        final_prompt = generate_locked_prompt("user", background, pose, phrase)

        # ✅ Generate image with DALL·E 3
        image_response = openai.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            n=1,
            size="1024x1024",
            response_format="url"
        )

        image_url = image_response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

# ✅ Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
