# Generated by Django 5.1.7 on 2025-04-04 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyectowebapp', '0008_medicion_color_uv'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicion',
            name='ubicacion_id',
            field=models.IntegerField(default=0),
        ),
    ]
