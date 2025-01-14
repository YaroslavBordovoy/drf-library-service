import enum

import stripe
from django.conf import settings
from django.db import models


STRIPE_URL = "http://127.0.0.1:8000/"
stripe.api_key = settings.STRIPE_SECRET_KEY


def calculate_sum(daily_fee, expected_date, borrow_date):
    book_price = daily_fee
    days_to_pay = (expected_date - borrow_date).days
    return book_price * days_to_pay


def get_stripe_data(money_to_pay, title, borrowing_id):
    """
    The function creates instances of stripe
    and by them creates a session for payment.
    Returns session id and session url.
    """
    product = stripe.Product.create(
        name=title
    )  # create stripe product with title of book
    stripe_product_id = product.id  # assign the value

    price = stripe.Price.create(  # create stripe price
        unit_amount=int(money_to_pay * 100),
        currency="usd",
        product=stripe_product_id,
    )
    stripe_price_id = price.id  # assign the value
    session = stripe.checkout.Session.create(  # create the session
        payment_method_types=["card"],
        line_items=[
            {
                "price": stripe_price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"{STRIPE_URL}api/payments/{borrowing_id}/success/",
        cancel_url=f"{STRIPE_URL}api/payments/{borrowing_id}/cancel/",
    )
    return session.id, session.url


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
        to="borrowing_service.Borrowing",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    session_url = models.URLField(max_length=511, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.money_to_pay = calculate_sum(
            self.borrowing.book.daily_fee,
            self.borrowing.expected_return_date,
            self.borrowing.borrow_date,
        )

        self.session_id, self.session_url = (
            get_stripe_data(  # assign the values of url and id from the function
                money_to_pay=self.money_to_pay,
                title=self.borrowing.book.title,
                borrowing_id=self.borrowing.id,
            )
        )
        return super(Payment, self).save(*args, **kwargs)
