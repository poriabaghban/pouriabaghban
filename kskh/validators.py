import os

from django.core.exceptions import ValidationError


ALLOWED_KSKH_EXTENSIONS = {
    ".apk",
    ".apks",
    ".aab",
    ".xapk",
    ".ipa",
    ".exe",
    ".conf",
    ".config",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".ovpn",
}

FORBIDDEN_TEXT_CHARS = ("<", ">", "}", '"', "'")


def validate_clean_text(value):
    if value is None:
        return
    if any(char in str(value) for char in FORBIDDEN_TEXT_CHARS):
        raise ValidationError("لطفا کاراکترهای غیرمجاز را حذف کنید.")


def validate_kskh_file(file_obj):
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_KSKH_EXTENSIONS:
        raise ValidationError("این پسوند برای kskh مجاز نیست.")
    if file_obj.size > 300 * 1024 * 1024:
        raise ValidationError("حجم فایل نباید بیشتر از 300MB باشد.")
