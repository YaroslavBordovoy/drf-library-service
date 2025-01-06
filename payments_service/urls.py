from django.urls import path
from .views import payment_success

app_name = "payment"

urlpatterns = [
    path("payment/<int:borrowing_id>/success/", payment_success, name="success-booking"),
    # другие URL
]
