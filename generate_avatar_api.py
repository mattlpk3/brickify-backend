from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import openai

app = Flask(__name__)

# 🔐 Your OpenAI API Key
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-...your-real-api-key..."

# 📁 Output folder
OUTPUT_DIR = "generated_avatars"
if not os.path.isdir(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 🧠 Use GPT-4o to generate prompt from user inputs
def generate_prompt(photo_path, background, pose, phrase):
    return f"Create a LEGO-style minifigure avatar inside a realistic plastic BRICKIFY toy box. The character should have a strong resemblance to the photo uploaded here: {photo_path}. The background should be {background}, the pose or accessory should be {pose}, and the name text at the bottom of the box should say '{phrase}'. On the top of the toy box, include the BRICKIFY logo and small icons for Instagram, TikTok, and X."  

# 🎨 Use DALL·E 3 to generate image from prompt
def generate_image(prompt):
    response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1
    )
    return response['data'][0]['url']

@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        # 1. Get inputs
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        # 2. Save uploaded photo locally
        filename = secure_filename(photo.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename
        filepath = os.path.join(OUTPUT_DIR, unique_filename)
        photo.save(filepath)

        # 3. Create prompt with GPT-4o (can be more advanced later)
        prompt = generate_prompt(filepath, background, pose, phrase)

        # 4. Generate image with DALL·E 3
        image_url = generate_image(prompt)

        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

