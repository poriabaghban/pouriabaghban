from django.core.exceptions import ValidationError


FORBIDDEN_USER_INPUT_CHARS = frozenset("%$<>{}")
FORBIDDEN_USER_INPUT_MESSAGE = "استفاده از کاراکترهای % $ < > { } مجاز نیست."


def contains_forbidden_user_input(value):
    return any(char in (value or "") for char in FORBIDDEN_USER_INPUT_CHARS)


def validate_no_forbidden_user_input(value):
    if contains_forbidden_user_input(value):
        raise ValidationError(FORBIDDEN_USER_INPUT_MESSAGE)
    return value
