import os
from flask import current_app
from werkzeug.utils import secure_filename
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file.filename == '':
        raise ValueError("No selected file")
    if not allowed_file(file.filename):
        raise ValueError("Invalid file type")

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    return file_path