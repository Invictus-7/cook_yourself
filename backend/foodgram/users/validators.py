import re

from django.core.exceptions import ValidationError

from foodgram.settings import INVALID_NAMES


def validate_username(name):
    for username in INVALID_NAMES:
        if re.match(username, name):
            raise ValidationError(f'"{name}" - недопустимое имя пользователя.')
    return name
