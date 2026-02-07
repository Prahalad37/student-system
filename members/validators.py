"""File upload validators for size and extension."""
import os

from django.core.exceptions import ValidationError

# Size limits in bytes
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB
MAX_DOCUMENT_SIZE = 5 * 1024 * 1024  # 5MB

ALLOWED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')
ALLOWED_DOCUMENT_EXTENSIONS = ('.pdf', '.jpg', '.jpeg', '.png')


def validate_image_file(uploaded_file):
    """
    Validate image upload: max 2MB, allowed jpg, jpeg, png, webp.
    Raises ValidationError on failure.
    """
    if not uploaded_file:
        return
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    if uploaded_file.size > MAX_IMAGE_SIZE:
        raise ValidationError(f"File too large. Maximum size is 2MB.")


def validate_document_file(uploaded_file):
    """
    Validate document upload: max 5MB, allowed pdf, jpg, jpeg, png.
    Raises ValidationError on failure.
    """
    if not uploaded_file:
        return
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            f"Invalid file type. Allowed: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"
        )
    if uploaded_file.size > MAX_DOCUMENT_SIZE:
        raise ValidationError(f"File too large. Maximum size is 5MB.")
