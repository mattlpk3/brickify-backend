from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# ✅ OpenAI API Key securely
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-..."

# ✅ GPT-4o Prompt Template Filler
async def fill_prompt_with_gpt4o(background, pose, phrase):
    system_prompt = """
You are a helpful assistant that generates a BRICKIFY image prompt by inserting user-provided variables into a locked template.
The structure must NEVER change. Just fill in the user inputs exactly where they belong.
Here is the locked prompt:

"""
Generate a full 3D LEGO-style avatar figure inside a LEGO-style brick box with a transparent background. The box must include:
- The BRICKIFY logo at the top in a brick-style font
- Just below it, small LEGO-styled icons for @, Instagram, TikTok, and X
- At the bottom, display the phrase: '{phrase}'
- Background must be: {background}
- Pose or accessory must be: {pose}
- The LEGO figure inside must look like the uploaded photo and have a strong facial resemblance.
Do not change the box structure or elements — always follow the locked BRICKIFY layout.
"""

    user_input = f"""
Background: {background}
Pose or Accessory: {pose}
Phrase: {phrase}
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    return response.choices[0].message.content.strip()

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

        # 🔁 Fill in locked prompt using GPT-4o
        final_prompt = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You only fill in variables in this locked BRICKIFY prompt structure. Do NOT change any wording, only inject variables."},
                {"role": "user", "content": f"Fill in this:
Generate a full 3D LEGO-style avatar figure inside a LEGO-style brick box with a transparent background. The box must include:
- The BRICKIFY logo at the top in a brick-style font
- Just below it, small LEGO-styled icons for @, Instagram, TikTok, and X
- At the bottom, display the phrase: '{phrase}'
- Background must be: {background}
- Pose or accessory must be: {pose}
- The LEGO figure inside must look like the uploaded photo and have a strong facial resemblance.
Do not change the box structure or elements — always follow the locked BRICKIFY layout."}
            ]
        ).choices[0].message.content.strip()

        # ✅ Generate image from DALL-E
        image_response = openai.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        image_url = image_response.data[0].url

        return jsonify({"success": 1, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": 0, "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
