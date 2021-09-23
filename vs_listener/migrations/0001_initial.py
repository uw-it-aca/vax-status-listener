# Generated by Django 3.2.7 on 2021-09-22 05:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=32, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Envelope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SlugField(choices=[('signed', 'signed'), ('completed', 'completed'), ('declined', 'declined'), ('voided', 'voided')], max_length=12)),
                ('reason', models.CharField(max_length=64, null=True)),
                ('guid', models.CharField(max_length=32, unique=True)),
                ('status_changed_date', models.DateTimeField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('processed_date', models.DateTimeField(null=True)),
                ('processed_status_code', models.CharField(max_length=3, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vs_listener.user')),
            ],
        ),
    ]
