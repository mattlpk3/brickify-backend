from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# ✅ OpenAI API Key securely
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-..."

# ✅ Generate final prompt with BRICKIFY official locked format
def generate_prompt(background, pose, phrase):
    return f"""
    Generate a full 3D LEGO-style avatar figure inside a LEGO-style brick box with a transparent background. The box must include:
    - The BRICKIFY logo at the top in a brick-style font
    - Just below it, small LEGO-styled icons for @, Instagram, TikTok, and X
    - At the bottom, display the phrase: '{phrase}'
    - Background must be: {background}
    - Pose or accessory must be: {pose}
    - The LEGO figure inside must look like the uploaded photo and have a strong facial resemblance.
    Do not change the box structure or elements — always follow the locked BRICKIFY layout.
    """

# ✅ Call DALL·E 3 API to generate the image
async def generate_image(prompt):
    response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    n=1,
    size="1024x1024",
    response_format="url",
    style="vivid",
    transparent=True  # 💡 Important for transparency
)
    )
    return response.data[0].url


# ✅ API endpoint to generate avatar
@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        if not all([photo, background, pose, phrase]):
            return jsonify({"success": 0, "message": "Missing required fields"})

        prompt = generate_prompt(background, pose, phrase)

        # ✅ Generate image from prompt only — do NOT pass image or transparency
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        image_url = response.data[0].url

        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

