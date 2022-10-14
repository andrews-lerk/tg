# Generated by Django 4.1.2 on 2022-10-06 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_usersessions'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='session_files/%Y/%m/%d/%H/%M/%S/')),
            ],
        ),
        migrations.AlterField(
            model_name='usersessions',
            name='files',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.fileset'),
        ),
    ]
