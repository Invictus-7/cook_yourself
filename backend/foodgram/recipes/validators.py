import re

from django.core.exceptions import ValidationError


def color_validator(input_color):
    if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', input_color):
        return input_color
    raise ValidationError(f'"{input_color}" не является цветом формата HEX.')


def slug_validator(input_slug):
    if re.match(r'^[-a-zA-Z0-9_]+', input_slug):
        return input_slug
    raise ValidationError(f'Слаг формата "{input_slug}" недопустим.')


def validate_cooking_time(time):
    pass
