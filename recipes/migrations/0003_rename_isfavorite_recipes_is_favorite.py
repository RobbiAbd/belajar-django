# Generated by Django 4.1 on 2024-08-14 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_recipes_isfavorite'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipes',
            old_name='isFavorite',
            new_name='is_favorite',
        ),
    ]
