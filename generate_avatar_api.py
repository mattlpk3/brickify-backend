from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

# Set your OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-..."

def generate_prompt(background, pose, phrase):
    return f"""
Create a 3D LEGO-style avatar of the person in the uploaded image. The figure must closely resemble their face and wear appropriate LEGO-style features. Pose the figure in a dynamic way based on the input provided. Place it inside a LEGO-style 3D red brick box with a transparent background and a {background} scene. The top of the box must say 'BRICKIFY' in a bold LEGO-style font. Directly underneath, show these icons in this exact order: @ symbol, Instagram logo, TikTok logo, X (Twitter) logo — small and clean. At the bottom, show a yellow LEGO-style nameplate with the following name or phrase: {phrase}. The box must include 3D brick studs on top and feel like a real LEGO box. Style must remain consistent, professional, and unique to BRICKIFY and around brick should be transparent background everytime.
"""

@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"}), 400

        prompt = generate_prompt(background, pose, phrase)

        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            response_format="url"
        )

        image_url = response.data[0].url
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        # This will return valid JSON instead of HTML error page
        return jsonify({"success": 0, "message": f"Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
