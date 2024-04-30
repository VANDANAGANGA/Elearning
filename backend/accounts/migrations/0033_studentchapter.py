# Generated by Django 4.2.6 on 2024-04-16 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_remove_course_end_date_remove_course_price_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentChapter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_completed', models.BooleanField(default=True)),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.chapter')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.studentprofile')),
            ],
        ),
    ]
