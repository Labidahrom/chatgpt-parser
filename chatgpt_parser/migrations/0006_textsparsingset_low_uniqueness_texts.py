# Generated by Django 4.2.4 on 2023-09-02 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgpt_parser', '0005_textsparsingset_failed_texts'),
    ]

    operations = [
        migrations.AddField(
            model_name='textsparsingset',
            name='low_uniqueness_texts',
            field=models.TextField(null=True),
        ),
    ]
