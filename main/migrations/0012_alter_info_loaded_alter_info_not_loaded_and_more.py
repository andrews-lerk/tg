# Generated by Django 4.1.2 on 2022-10-10 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_info_user_alter_user_is_loading_process_started'),
    ]

    operations = [
        migrations.AlterField(
            model_name='info',
            name='loaded',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='info',
            name='not_loaded',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='info',
            name='read_dialogs',
            field=models.IntegerField(default=0),
        ),
    ]
