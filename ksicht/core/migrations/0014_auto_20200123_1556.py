# Generated by Django 2.2.8 on 2020-01-23 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_event_reward_stickers"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sticker",
            options={
                "ordering": ("nr", "title"),
                "verbose_name": "Nálepka",
                "verbose_name_plural": "Nálepky",
            },
        ),
        migrations.AlterField(
            model_name="event",
            name="reward_stickers",
            field=models.ManyToManyField(
                blank=True,
                help_text="Každý účastník získá zvolené nálepky. Uděleny budou v rámci série, která datumově následuje po akci.",
                related_name="event_uses",
                to="core.Sticker",
                verbose_name="Nálepky pro účastníky",
            ),
        ),
    ]
