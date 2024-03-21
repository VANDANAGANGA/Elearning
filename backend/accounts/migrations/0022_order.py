# Generated by Django 4.2.6 on 2023-12-19 05:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_questions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_amount', models.CharField(max_length=25)),
                ('order_payment_id', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=False)),
                ('order_date', models.DateTimeField(auto_now=True)),
                ('months', models.IntegerField(default=0)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.studentprofile')),
            ],
        ),
    ]