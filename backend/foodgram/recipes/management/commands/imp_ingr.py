import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open(
            f"{settings.BASE_DIR}/data/ingredients.csv",
            "r",
            encoding="utf-8",
        ) as file:
            file_reader = csv.reader(file)
            for row in file_reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit)
            file.close()

        tags = (
            ('Завтрак', '#AFB83B', 'breakfast'),
            ('Обед', '#FAD000', 'dinner'),
            ('Ужин', '#FF9933', 'supper'),
        )

        for tag in tags:
            name, color, slug = tag
            Tag.objects.get_or_create(
                name=name,
                color=color,
                slug=slug
            )
        self.stdout.write(self.style.SUCCESS('Ингредиенты и тэги добавлены'))
