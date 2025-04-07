from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import tempfile

app = Flask(__name__)
CORS(app)

# 🔐 Your OpenAI API Key
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-...your-real-api-key..."

# 🧠 Generate prompt
def generate_prompt(background, pose, phrase):
    return f"""
    Create a LEGO-style minifigure avatar inside a realistic plastic BRICKIFY toy box.
    Background: {background}
    Pose or accessory: {pose}
    Name on box: {phrase}
    Include: Strong facial resemblance, BRICKIFY logo, and icons for Instagram, TikTok, and X on top.
    """

# 🎨 DALL·E 3 image generation
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

        # (Optional) Use uploaded photo name for similarity, but not needed if just prompt-based
        prompt = generate_prompt(background, pose, phrase)
        image_url = generate_image(prompt)

        return jsonify({"success": 1, "image_url": image_url})
    
    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
