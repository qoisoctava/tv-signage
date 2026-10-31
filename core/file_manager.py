import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    images = current_app.config['ALLOWED_IMAGE_EXTENSIONS']
    videos = current_app.config['ALLOWED_VIDEO_EXTENSIONS']
    return ext in images | videos


def get_file_type(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext in current_app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return 'image'
    if ext in current_app.config['ALLOWED_VIDEO_EXTENSIONS']:
        return 'video'
    return None


def save_upload(file):
    """
    Simpan file upload ke UPLOAD_FOLDER.
    Return dict { filename, path, type, size } atau None jika gagal.
    """
    if not file or file.filename == '':
        return None

    original = secure_filename(file.filename)
    if not allowed_file(original):
        return None

    ext = original.rsplit('.', 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = current_app.config['UPLOAD_FOLDER']
    abs_path = os.path.join(upload_dir, unique_name)
    file.save(abs_path)

    size = os.path.getsize(abs_path)
    # path relatif dari static/ untuk url_for / serve langsung
    rel_path = f"uploads/{unique_name}"

    return {
        'filename': unique_name,
        'original_name': original,
        'path': rel_path,
        'type': get_file_type(original),
        'size': size,
    }


def delete_upload(path):
    """Hapus file media dari disk. path = relatif dari static/."""
    static_dir = os.path.join(os.path.dirname(current_app.config['UPLOAD_FOLDER']))
    abs_path = os.path.join(static_dir, path)
    if os.path.exists(abs_path):
        os.remove(abs_path)
        return True
    return False


def format_size(size_bytes):
    """Konversi bytes ke string human-readable."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
