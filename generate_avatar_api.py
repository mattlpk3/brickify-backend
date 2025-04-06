from flask_cors import CORS
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import openai

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

OUTPUT_DIR = "generated_avatars"
if not os.path.isdir(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_prompt(photo_path, background, pose, phrase):
    return f"Create a LEGO-style minifigure avatar inside a realistic plastic BRICKIFY toy box. The character should have a strong resemblance to the photo uploaded here: {photo_path}. The background should be {background}, the pose or accessory should be {pose}, and the name text at the bottom of the box should say '{phrase}'. On the top of the toy box, include the BRICKIFY logo and small icons for Instagram, TikTok, and X."  

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
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        filename = secure_filename(photo.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename
        filepath = os.path.join(OUTPUT_DIR, unique_filename)
        photo.save(filepath)

        prompt = generate_prompt(filepath, background, pose, phrase)
        image_url = generate_image(prompt)

        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
