from django.urls import path
from payments_service.views import payment_success


app_name = "payment"

urlpatterns = [
    path("<int:borrowing_id>/success/", payment_success, name="success-booking"),
]
