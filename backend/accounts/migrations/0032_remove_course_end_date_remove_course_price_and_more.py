# Generated by Django 4.2.6 on 2024-03-19 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0031_teacherprofile_account'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='course',
            name='price',
        ),
        migrations.RemoveField(
            model_name='course',
            name='start_date',
        ),
        migrations.AddField(
            model_name='course',
            name='created_at',
            field=models.DateField(auto_now=True),
        ),
    ]
