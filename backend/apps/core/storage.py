from io import BytesIO
from pathlib import Path

from django.conf import settings
from supabase import Client, create_client


def get_supabase_client() -> Client | None:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def _local_media_url(path: str, request=None) -> str:
    relative = f"{settings.MEDIA_URL.rstrip('/')}/{path.replace(chr(92), '/')}"
    if request is not None:
        return request.build_absolute_uri(relative)
    return relative


def _save_local_file(path: str, data: bytes) -> bool:
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if not media_root:
        return False
    full_path = Path(media_root) / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(data)
    return True


def upload_file(
    path: str,
    data: bytes,
    content_type: str = 'application/octet-stream',
    *,
    request=None,
) -> str | None:
    client = get_supabase_client()
    if client:
        bucket = settings.SUPABASE_STORAGE_BUCKET
        client.storage.from_(bucket).upload(
            path,
            data,
            file_options={'content-type': content_type, 'upsert': 'true'},
        )
        return client.storage.from_(bucket).get_public_url(path)

    if _save_local_file(path, data):
        return _local_media_url(path, request)
    return None


def upload_bytesio(
    path: str,
    file_obj: BytesIO,
    content_type: str = 'application/octet-stream',
    *,
    request=None,
) -> str | None:
    return upload_file(path, file_obj.getvalue(), content_type, request=request)


def get_signed_url(path: str, expires_in: int = 3600) -> str | None:
    client = get_supabase_client()
    if not client:
        return None
    bucket = settings.SUPABASE_STORAGE_BUCKET
    result = client.storage.from_(bucket).create_signed_url(path, expires_in)
    return result.get('signedURL')
