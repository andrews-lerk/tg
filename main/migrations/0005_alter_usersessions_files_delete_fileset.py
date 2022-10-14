# Generated by Django 4.1.2 on 2022-10-06 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_fileset_alter_usersessions_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersessions',
            name='files',
            field=models.FileField(upload_to='session_files/%Y/%m/%d/%H/%M/%S/'),
        ),
        migrations.DeleteModel(
            name='FileSet',
        ),
    ]
