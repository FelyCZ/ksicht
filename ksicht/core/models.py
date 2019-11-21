import uuid
from django import forms
from datetime import date, datetime
from operator import attrgetter
from django.db import models
from django.core.validators import MinValueValidator

import pydash as py_
from cuser.models import AbstractCUser

from .constants import SCHOOLS


class User(AbstractCUser):
    def is_participant(self):
        return Participant.objects.filter(user=self).exists()

class GradeManager(models.Manager):
    def get_current(self, current=None):
        current_date = current or date.today()
        return self.filter(
            start_date__lte=current_date, end_date__gte=current_date
        ).first()


def default_grade_school_year():
    current_year = date.today()
    return f"{current_year.year}/{current_year.year + 1}"


def default_grade_start():
    return date(date.today().year, 8, 1)


def default_grade_end():
    return date(date.today().year + 1, 7, 31)


class Grade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school_year = models.CharField(
        verbose_name="Školní rok",
        max_length=50,
        null=False,
        db_index=True,
        unique=True,
        default=default_grade_school_year,
    )
    errata = models.TextField(verbose_name="Errata", null=False, blank=True)
    start_date = models.DateField(
        verbose_name="Začíná",
        null=False,
        blank=False,
        db_index=True,
        default=default_grade_start,
    )
    end_date = models.DateField(
        verbose_name="Končí",
        null=False,
        blank=False,
        db_index=True,
        default=default_grade_end,
    )

    objects = GradeManager()

    class Meta:
        verbose_name = "Ročník"
        verbose_name_plural = "Ročníky"

    def __str__(self):
        return self.school_year

    def full_clean(self, *args, **kwargs):
        """Validate the grade.

        Make sure 'valid_through' does not overlap."""
        super().full_clean(*args, **kwargs)

        if self.start_date is not None and self.end_date is not None:
            g = (
                Grade.objects.filter(
                    models.Q(
                        start_date__lte=self.start_date, end_date__gte=self.start_date,
                    )
                    | models.Q(
                        start_date__lte=self.end_date, end_date__gte=self.end_date,
                    )
                )
                .exclude(pk=self.pk)
                .first()
            )

            if g:
                raise forms.ValidationError(
                    f"Datum konání se překrývá s ročníkem '{g}'."
                )

    def get_current_series(self):
        """Return first series that can still accept solution submissions from participants."""
        return (
            py_.chain(list(self.series.all()))
            .filter(attrgetter("accepts_solution_submissions"))
            .sort(key=attrgetter("submission_deadline"))
            .head()
            .value()
        )


class GradeSeries(models.Model):
    SERIES_CHOICES = (
        ("1", "1."),
        ("2", "2."),
        ("3", "3."),
        ("4", "4."),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grade = models.ForeignKey(
        Grade, verbose_name="Ročník", on_delete=models.CASCADE, related_name="series"
    )
    series = models.CharField(
        verbose_name="Série",
        max_length=1,
        choices=SERIES_CHOICES,
        null=False,
        db_index=True,
    )
    submission_deadline = models.DateTimeField(
        verbose_name="Deadline pro odeslání řešení", null=False
    )
    task_file = models.FileField(
        verbose_name="Brožura", upload_to="rocniky/zadani/", null=True, blank=True
    )

    class Meta:
        unique_together = ("grade", "series")
        verbose_name = "Série"
        verbose_name_plural = "Série"
        ordering = ("grade", "series")

    def __str__(self):
        return f"{self.get_series_display()} série"

    @property
    def accepts_solution_submissions(self):
        return self.task_file is not None and self.submission_deadline > datetime.now(
            self.submission_deadline.tzinfo
        )

    @property
    def has_results_published(self):
        return True


class Task(models.Model):
    TASK_NR_CHOICES = (
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(
        GradeSeries,
        verbose_name="Série",
        on_delete=models.PROTECT,
        related_name="tasks",
    )
    nr = models.CharField(
        verbose_name="Číslo",
        max_length=1,
        choices=TASK_NR_CHOICES,
        null=False,
        db_index=True,
    )
    title = models.CharField(verbose_name="Název", max_length=150, null=False)
    points = models.PositiveIntegerField(
        verbose_name="Max. počet bodů",
        null=False,
        blank=False,
        validators=(MinValueValidator(1),),
    )

    class Meta:
        unique_together = ("series", "nr")
        verbose_name = "Úloha"
        verbose_name_plural = "Úlohy"
        ordering = ("series", "nr")

    def __str__(self):
        return f"Úloha č. {self.nr}"


class Participant(models.Model):
    COUNTRY_CHOICES = (
        ("other", "-- jiný --"),
        ("cz", "Česko"),
        ("sk", "Slovensko"),
    )
    GRADE_CHOICES = (
        ("4", "4"),
        ("3", "3"),
        ("2", "2"),
        ("1", "1"),
        ("l", "nižší"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="participant_profile",
    )

    phone = models.CharField(verbose_name="Telefon", max_length=20, null=True)
    street = models.CharField(verbose_name="Ulice", max_length=100, null=False)
    city = models.CharField(verbose_name="Obec", max_length=100, null=False)
    zip_code = models.CharField(verbose_name="PSČ", max_length=10, null=False)
    country = models.CharField(
        verbose_name="Stát", max_length=10, null=False, choices=COUNTRY_CHOICES
    )

    school = models.CharField(
        verbose_name="Škola", max_length=80, null=False, choices=SCHOOLS
    )
    school_year = models.CharField(
        verbose_name="Ročník", max_length=1, null=False, choices=GRADE_CHOICES,
    )

    school_alt_name = models.CharField(
        verbose_name="Název školy", max_length=80, null=True, blank=True
    )
    school_alt_street = models.CharField(
        verbose_name="Ulice školy", max_length=100, null=True, blank=True
    )
    school_alt_city = models.CharField(
        verbose_name="Obec školy", max_length=100, null=True, blank=True
    )
    school_alt_zip_code = models.CharField(
        verbose_name="PSČ školy", max_length=10, null=True, blank=True
    )

    applications = models.ManyToManyField(
        Grade, verbose_name="Přihlášky", related_name="participants", blank=True, through="GradeApplication"
    )

    class Meta:
        verbose_name = "Řešitel"
        verbose_name_plural = "Řešitelé"

    def __str__(self):
        return f"Profil účastníka pro <{self.user}>"


class GradeApplication(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Přihláška do ročníku"
        verbose_name_plural = "Přihlášky do ročníku"

    def __str__(self):
        return f"Přihláška <{self.participant.user}> do ročníku <{self.grade}>"


class TaskSolutionSubmission(models.Model):
    application = models.ForeignKey(GradeApplication, verbose_name="Přihláška", null=False, blank=False, on_delete=models.CASCADE, related_name="solution_submissions")
    task = models.ForeignKey(Task, verbose_name="Úloha", null=False, blank=False, on_delete=models.PROTECT, related_name="solution_submissions")
    file = models.FileField(verbose_name="Soubor s řešením", upload_to="rocniky/reseni/", null=False, blank=False)

    class Meta:
        verbose_name = "Odevzdané řešení"
        verbose_name_plural = "Odevzdaná řešení"

    def __str__(self):
        return f"Řešení <{self.task}> pro přihlášku <{self.application_id}>"
