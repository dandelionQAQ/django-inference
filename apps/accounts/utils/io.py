import os
import uuid


def avatar_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    user_part = f"user_{instance.pk}" if instance.pk else "temp"
    return f"accounts/avatars/{user_part}/{uuid.uuid4().hex}{ext}"


def safe_delete_file(file_field):
    if not file_field:
        return
    try:
        storage = file_field.storage
        name = file_field.name
        if name and storage.exists(name):
            file_field.delete(save=False)
    except Exception:
        pass
