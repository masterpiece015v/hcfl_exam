# Generated by Django 3.2.14 on 2022-07-18 04:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0004_alter_test_answers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='file_path',
            new_name='file_name',
        ),
    ]
