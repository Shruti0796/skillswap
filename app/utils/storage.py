"""
File storage for profile pictures and session materials.

Files are stored in Supabase Storage.

Bucket:
    skillswap-uploads

Folders:
    profile-pics/
    session-materials/
"""

import os
import uuid

from flask import current_app
from supabase import create_client


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".txt",
    ".md",
}


def _safe_filename(original_name, allowed_extensions, default_ext):
    ext = os.path.splitext(original_name or "")[1].lower()

    if ext not in allowed_extensions:
        ext = default_ext

    return f"{uuid.uuid4().hex}{ext}"


def _get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not url:
        raise RuntimeError("SUPABASE_URL is not configured")

    if not key:
        raise RuntimeError("SUPABASE_SERVICE_KEY is not configured")

    return create_client(url, key)


def _upload(file_storage, subfolder, filename, content_type):
    supabase = _get_supabase()

    bucket = os.environ.get(
        "SUPABASE_STORAGE_BUCKET",
        "skillswap-uploads"
    )

    key = f"{subfolder}/{filename}"

    file_bytes = file_storage.read()

    supabase.storage.from_(bucket).upload(
        key,
        file_bytes,
        {
            "content-type": content_type,
            "upsert": False,
        },
    )

    public_url = supabase.storage.from_(bucket).get_public_url(key)

    return public_url


def save_profile_picture(file_storage):
    """Upload profile picture to Supabase Storage."""

    filename = _safe_filename(
        file_storage.filename,
        IMAGE_EXTENSIONS,
        ".png",
    )

    return _upload(
        file_storage,
        "profile-pics",
        filename,
        file_storage.mimetype or "image/png",
    )


def save_session_material(file_storage):
    """Upload session material to Supabase Storage."""

    filename = _safe_filename(
        file_storage.filename,
        DOCUMENT_EXTENSIONS,
        ".pdf",
    )

    return _upload(
        file_storage,
        "session-materials",
        filename,
        file_storage.mimetype or "application/pdf",
    )