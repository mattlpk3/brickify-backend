from flask_cors import CORS
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import openai

app = Flask(__name__)
CORS(app)

# 🔐 Load OpenAI API key securely
openai.api_key = os.environ.get("OPENAI_API_KEY") or "your-actual-api-key"

# 📁 Output folder
OUTPUT_DIR = "generated_avatars"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🧠 Generate prompt from user input
def generate_prompt(photo_path, background, pose, phrase):
    return f"Create a LEGO-style minifigure avatar inside a realistic BRICKIFY toy box. Match the uploaded photo here: {photo_path}. Background: {background}. Pose or Accessory: {pose}. Phrase: '{phrase}'. Include the BRICKIFY logo and small social icons (Instagram, TikTok, X) on top of the toy box."

# 🎨 Use DALL·E 3 to generate image
def generate_image(prompt):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    return response.data[0].url

@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        filename = secure_filename(photo.filename)
        filepath = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}_{filename}")
        photo.save(filepath)

        prompt = generate_prompt(filepath, background, pose, phrase)
        image_url = generate_image(prompt)

        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
