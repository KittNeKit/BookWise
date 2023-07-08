from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.exceptions import ValidationError


class Book(models.Model):
    class CoverChoice(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=50, choices=CoverChoice.choices)
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self) -> str:
        return self.title

    def clean(self):
        if self.inventory < 0:
            raise ValidationError(f"Do not enough {self.title} book in inventory")

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Book, self).save(
            force_insert, force_update, using, update_fields
        )
