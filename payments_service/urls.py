from django.urls import path
from .views import PaymentSuccessView, PaymentCancelView, StartPaymentView, create_checkout_session

app_name = "payment"
urlpatterns = [
    path('payments/<int:pk>/success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('payments/<int:pk>/cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('payments/<int:pk>/start/', StartPaymentView.as_view(), name='payment-start'),
    path('payments/test/', create_checkout_session, name='test'),

]
