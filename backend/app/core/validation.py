# backend/app/core/validation.py
import re
from typing import Optional

from app.core.exceptions import ValidationError
from app.middleware.simple_logging import get_correlation_id


def validate_email(email: str) -> str:
    """Validate and sanitize email"""
    if not email or len(email) > 254:
        raise ValidationError("Invalid email length", "email", get_correlation_id())

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email.strip().lower()):
        raise ValidationError("Invalid email format", "email", get_correlation_id())

    return email.strip().lower()


def validate_filename(filename: str) -> str:
    """Validate and sanitize filename"""
    if not filename or len(filename) > 255:
        raise ValidationError(
            "Invalid filename length", "filename", get_correlation_id()
        )

    # Remove dangerous characters
    dangerous_chars = ["/", "\\", "..", "<", ">", ":", '"', "|", "?", "*"]
    for char in dangerous_chars:
        if char in filename:
            raise ValidationError(
                f"Filename contains invalid character: {char}",
                "filename",
                get_correlation_id(),
            )

    return filename.strip()


def sanitize_text_input(text: str, max_length: int = 1000) -> str:
    """Sanitize general text input"""
    if not text:
        return ""

    if len(text) > max_length:
        raise ValidationError(
            f"Text too long (max {max_length} characters)", "text", get_correlation_id()
        )

    # Remove potential XSS characters but keep basic formatting
    text = text.replace("<", "&lt;").replace(">", "&gt;")

    return text.strip()


def validate_uuid(uuid_str: str, field_name: str = "id") -> str:
    """Validate UUID format"""
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

    if not re.match(uuid_pattern, uuid_str.lower()):
        raise ValidationError(
            f"Invalid {field_name} format", field_name, get_correlation_id()
        )

    return uuid_str.lower()
