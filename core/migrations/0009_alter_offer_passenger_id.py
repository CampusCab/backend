# Generated by Django 5.0.4 on 2024-05-19 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_offer_passenger_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="offer",
            name="passenger_id",
            field=models.IntegerField(),
        ),
    ]