from django.db import models
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
