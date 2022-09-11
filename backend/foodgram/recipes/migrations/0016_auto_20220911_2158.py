# Generated by Django 2.2.16 on 2022-09-11 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0015_auto_20220911_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to='recipes.Recipe', verbose_name='Рецепт'),
        ),
    ]
