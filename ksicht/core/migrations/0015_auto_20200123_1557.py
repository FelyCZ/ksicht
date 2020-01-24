# Generated by Django 2.2.8 on 2020-01-23 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_auto_20200123_1556"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="task",
            options={
                "ordering": ("series", "nr"),
                "permissions": (("solution_export", "Export odevzdaných úloh"),),
                "verbose_name": "Úloha",
                "verbose_name_plural": "Úlohy",
            },
        ),
        migrations.AddField(
            model_name="task",
            name="nr",
            field=models.CharField(
                choices=[
                    ("1", "1."),
                    ("2", "2."),
                    ("3", "3."),
                    ("4", "4."),
                    ("5", "5."),
                ],
                db_index=True,
                default=1,
                max_length=1,
                verbose_name="Číslo úlohy",
            ),
            preserve_default=False,
        ),
    ]
