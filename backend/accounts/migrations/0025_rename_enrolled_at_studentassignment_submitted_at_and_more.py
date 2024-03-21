# Generated by Django 4.2.6 on 2023-12-27 15:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_studentassignment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studentassignment',
            old_name='enrolled_at',
            new_name='submitted_at',
        ),
        migrations.AddField(
            model_name='studentassignment',
            name='verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='studentassignment',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.assignment'),
        ),
    ]
