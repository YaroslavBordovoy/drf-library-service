from django.db import models
from django.core.exceptions import ValidationError
from enum import Enum


class Cover(Enum):
    HARD = "HARD"
    SOFT = "SOFT"


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=4,
        choices=[(cover.name, cover.value) for cover in Cover]
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.title

    def clean(self):
        if self.inventory < 0:
            raise ValidationError("Inventory cannot be negative.")

        if self.daily_fee <= 0:
            raise ValidationError("Daily fee must be greater than 0.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
