from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)

# Create a folder for generated images
OUTPUT_DIR = "generated_avatars_storage"
OUTPUT_DIR = "generated_avatars_storage"


# ✅ Safe check to prevent FileExistsError
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
elif not os.path.isdir(OUTPUT_DIR):
    raise Exception(f"'{OUTPUT_DIR}' exists but is not a directory")



@app.route('/api/generate-avatar', methods=['POST'])
def generate_avatar():
    try:
        # Get form fields
        photo = request.files.get('photo')
        background = request.form.get('background')
        pose = request.form.get('pose')
        phrase = request.form.get('phrase')

        # Basic validation
        if not all([photo, background, pose, phrase]):
            return jsonify({ "success": 0, "message": "Missing required fields" })

        # Save uploaded image
        filename = secure_filename(photo.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename
        filepath = os.path.join(OUTPUT_DIR, unique_filename)
        photo.save(filepath)

        # ---- MOCK GENERATION (you'll replace this later with AI image generation logic) ----
        # Just re-use uploaded photo as output for now
        output_url = f"https://brickify-api.onrender.com/static/{unique_filename}"

        # Make sure output file is available in a static folder
        return jsonify({ "success": 1, "image_url": output_url })

    except Exception as e:
        return jsonify({ "success": 0, "message": str(e) })


if __name__ == '__main__':
    app.run(debug=True)
