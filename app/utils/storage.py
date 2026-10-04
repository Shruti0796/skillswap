"""
File storage for profile pictures AND session materials (notes/PDFs).
- If S3_BUCKET is set in config, uploads go to S3 and a public URL is returned.
- Otherwise, files are saved locally to app/static/uploads/ (fine for dev/local demo).

Files are never overwritten and never deleted by the app, so anything
uploaded as session notes stays reachable at the same URL indefinitely.
"""
import os
import uuid
from flask import current_app

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt", ".md"}


def _safe_filename(original_name, allowed_extensions, default_ext):
    ext = os.path.splitext(original_name or "")[1].lower()
    if ext not in allowed_extensions:
        ext = default_ext
    return f"{uuid.uuid4().hex}{ext}"


def _upload(file_storage, subfolder, filename, content_type):
    bucket = current_app.config.get("S3_BUCKET")

    if bucket:
        import boto3
        s3 = boto3.client("s3", region_name=current_app.config["AWS_REGION"])
        key = f"{subfolder}/{filename}"
        s3.upload_fileobj(
            file_storage, bucket, key, ExtraArgs={"ContentType": content_type}
        )
        region = current_app.config["AWS_REGION"]
        return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    subfolder_path = os.path.join(upload_folder, subfolder)
    os.makedirs(subfolder_path, exist_ok=True)
    file_storage.save(os.path.join(subfolder_path, filename))
    return f"/static/uploads/{subfolder}/{filename}"


def save_profile_picture(file_storage):
    """Returns a URL/path to store on the user's profile_pic_url."""
    filename = _safe_filename(file_storage.filename, IMAGE_EXTENSIONS, ".png")
    return _upload(file_storage, "profile-pics", filename, file_storage.mimetype or "image/png")


def save_session_material(file_storage):
    """Returns a URL/path for a notes/PDF file attached to a session."""
    filename = _safe_filename(file_storage.filename, DOCUMENT_EXTENSIONS, ".pdf")
    return _upload(file_storage, "session-materials", filename, file_storage.mimetype or "application/pdf")
