# Generated by Django 4.1.2 on 2022-10-11 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_info_all_dialogs'),
    ]

    operations = [
        migrations.AddField(
            model_name='dialog',
            name='is_last_message_out',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
