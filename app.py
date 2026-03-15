import json
import os
import uuid
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from caption_model import generate_caption

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
DATA_DIR = BASE_DIR / "data"
CAPTIONS_FILE = DATA_DIR / "captions.json"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")


# Ensure required directories/files are available before handling requests.
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
if not CAPTIONS_FILE.exists():
    CAPTIONS_FILE.write_text("[]", encoding="utf-8")


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_captions() -> list[dict]:
    try:
        with CAPTIONS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_captions(entries: list[dict]) -> None:
    with CAPTIONS_FILE.open("w", encoding="utf-8") as file:
        json.dump(entries, file, indent=2)


@app.route("/")
def index():
    """Home route: show app overview and navigation actions."""
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_image():
    """Upload route: save image, generate caption with BLIP, persist metadata."""
    if request.method == "POST":
        if "image" not in request.files:
            flash("No image part found in the form.", "danger")
            return redirect(request.url)

        file = request.files["image"]
        if file.filename == "":
            flash("Please choose an image file.", "danger")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Unsupported file type. Upload PNG, JPG, JPEG, GIF, or WEBP.", "warning")
            return redirect(request.url)

        original_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        saved_path = UPLOAD_DIR / unique_name
        file.save(saved_path)

        # ML integration: run BLIP captioning on the stored image path.
        caption = generate_caption(str(saved_path))

        entries = load_captions()
        entries.append(
            {
                "filename": unique_name,
                "original_filename": original_name,
                "caption": caption,
            }
        )
        save_captions(entries)

        flash("Image uploaded and caption generated.", "success")
        return redirect(url_for("gallery"))

    return render_template("upload.html")


@app.route("/gallery")
def gallery():
    """Gallery route: display uploaded images with generated captions."""
    entries = list(reversed(load_captions()))
    return render_template("gallery.html", entries=entries)


@app.route("/api/caption", methods=["POST"])
def caption_api():
    """Optional API route: accept an image and return caption JSON."""
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["image"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or unsupported image file."}), 400

    original_name = secure_filename(file.filename)
    temp_name = f"api_{uuid.uuid4().hex}_{original_name}"
    temp_path = UPLOAD_DIR / temp_name
    file.save(temp_path)

    try:
        caption = generate_caption(str(temp_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()

    return jsonify({"filename": original_name, "caption": caption})


if __name__ == "__main__":
    app.run(debug=True)
