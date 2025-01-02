from django.conf import settings
from django.db import models
from django.db.models import CASCADE
from rest_framework.exceptions import ValidationError


class Borrowing(models.Model):
    book = models.ForeignKey(
        "books_service.Book", on_delete=CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="borrowings"
    )
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)

    @staticmethod
    def validate_borrowing(borrow_date, expected_date):
        if expected_date < borrow_date:
            raise ValidationError(
                "Expected return date cannot be earlier than borrow date!"
            )

    def clean(self):
        Borrowing.validate_borrowing(
            self.borrow_date, self.expected_return_date
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.actual_return_date:
            return (
                f"{self.book.title} "
                f"borrowed {self.borrow_date} and "
                f"returned {self.actual_return_date}"
            )
        return (
            f"{self.book.title} "
            f"borrowed {self.borrow_date} and "
            f"expected to return {self.expected_return_date}"
        )
