from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://trenchmoney.online"])

# 🔐 Your OpenAI API Key
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-...your-real-api-key..."

# 🧠 Generate the prompt
def generate_prompt(image_url, background, pose, phrase):
    return f"""
    Create a LEGO-style minifigure avatar inside a BRICKIFY toy box. 
    The character should resemble the person in this photo: {image_url}.
    The background should be {background}, pose or accessory should be {pose}, 
    and the name text at the bottom of the box should say "{phrase}".
    The BRICKIFY logo and icons for Instagram, TikTok, and X must be on top of the box.
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

        # Save photo temporarily to Render's /tmp directory
        photo_path = f"/tmp/{photo.filename}"
        photo.save(photo_path)

        # Use GPT to generate image prompt
        prompt = generate_prompt("photo attached", background, pose, phrase)

        # Generate image from DALL·E 3
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = response['data'][0]['url']
        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
