import enum
from decimal import Decimal

import stripe
from django.db import models

from borrowing_service.models import Borrowing


class StatusChoices(enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class TypeChoices(enum.Enum):
    PAYMENT = "PAYMENT"
    FINE = "FINE"


class Payment(models.Model):
    status = models.CharField(
        max_length=7,
        choices=[
            (status.value, status.name.capitalize())
            for status in StatusChoices
        ],
        default=StatusChoices.PENDING.value,
    )
    type = models.CharField(
        max_length=7,
        choices=[
            (type_.value, type_.name.capitalize()) for type_ in TypeChoices
        ],
        default=TypeChoices.FINE.value,
    )
    borrowing = models.ForeignKey(
        to="borrowing_service.Borrowing", on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(blank=True, null=True)
    session_id = models.CharField(max_length=7, blank=True, null=True)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)

    @property
    def calculate_sum(self):
        book_price = self.borrowing.book.daily_fee

        # days_to_pay = (
        #     self.borrowing.expected_return_date - self.borrowing.borrow_date
        # )

        # self.money_to_pay = book_price * days_to_pay
        return 50

    def save(
        self,
        *args,
        **kwargs,
    ):
        # self.calculate_sum()

        if not self.stripe_product_id:
            product = stripe.Product.create(name=self.borrowing.book.title)
            self.stripe_product_id = product.id

        price = stripe.Price.create(
            unit_amount=Decimal(self.calculate_sum * 100),  # Stripe принимает сумму в центах
            currency='usd',
            product=self.stripe_product_id,
        )
        self.stripe_price_id = price.id

        super().save(*args, **kwargs)
        return super(Payment, self).save(*args, **kwargs)
