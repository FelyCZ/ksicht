# Generated by Django 2.2.10 on 2020-05-24 08:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_auto_20200510_0917"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="EventAttendee",
                    fields=[
                        (
                            "id",
                            models.AutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                    ],
                    options={"db_table": "core_event_attendees",},
                ),
                migrations.AlterField(
                    model_name="event",
                    name="attendees",
                    field=models.ManyToManyField(
                        blank=True,
                        through="core.EventAttendee",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Účastníci",
                    ),
                ),
                migrations.AddField(
                    model_name="eventattendee",
                    name="event",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.Event"
                    ),
                ),
                migrations.AddField(
                    model_name="eventattendee",
                    name="user",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AlterUniqueTogether(
                    name="eventattendee", unique_together={("user", "event")},
                ),
            ],
            database_operations=[],
        )
    ]