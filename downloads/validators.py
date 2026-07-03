from django.core.exceptions import ValidationError


FORBIDDEN_TEXT_CHARS = ('<', '>', '}', '/', '"', "'")
FORBIDDEN_TEXT_MESSAGE = (
    "Input contains forbidden characters: < > } / \" '. "
    "Please remove them and try again."
)


def validate_clean_text(value):
    if value is None:
        return
    text = str(value)
    if any(char in text for char in FORBIDDEN_TEXT_CHARS):
        raise ValidationError(FORBIDDEN_TEXT_MESSAGE)


def validate_text_fields(instance, field_names):
    errors = {}
    for field_name in field_names:
        try:
            value = getattr(instance, field_name)
        except AttributeError:
            continue
        try:
            validate_clean_text(value)
        except ValidationError as exc:
            errors[field_name] = exc.messages
    if errors:
        raise ValidationError(errors)
