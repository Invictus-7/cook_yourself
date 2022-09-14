import csv
import os

from django.apps import apps
from django.core.management import BaseCommand


BASE_DICT = {'ingredients': ['Ingredient', 'recipes', 'filepath']}


class Command(BaseCommand):

    def get_files(self, path):
        files = []
        for roots, dirs, file_names in os.walk(path):
            for file_name in file_names:
                if file_name.endswith('.csv'):
                    file_path = os.path.join(roots, file_name)
                    files.append(file_path)
        return files

    def transfer(self, base_item):
        model_name = BASE_DICT[base_item][0]
        app_name = BASE_DICT[base_item][1]
        file_path = BASE_DICT[base_item][2]

        model = apps.get_model(app_name, model_name)

        with open(file_path, 'r', encoding='UTF-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')

            header = ('name', 'measurement_unit')

            for element in reader:
                new_object_dict = {key: value for key, value in
                                   zip(header, element)}

                try:
                    model.objects.create(**new_object_dict)

                except ValueError:
                    self.stdout.write(
                        self.style.ERROR('Error while transferring data')
                    )

    def handle(self, *args, **options):
        files = self.get_files(os.getcwd())
        for file_path in files:
            file_name = os.path.basename(file_path).split('.', 1)[0]
            if file_name in BASE_DICT:
                BASE_DICT[file_name][2] = file_path

        self.transfer('ingredients')
