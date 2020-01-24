# Generated by Django 2.2.8 on 2020-01-24 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_auto_20200123_1613"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="event",
            options={
                "ordering": ("-start_date",),
                "permissions": (("export_event_attendees", "Export účastníků akce"),),
                "verbose_name": "Akce",
                "verbose_name_plural": "Akce",
            },
        ),
    ]
