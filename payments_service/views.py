import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.decorators import api_view

from borrowing_service.models import Borrowing
from .models import Payment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Payment



def create_stripe_payment_session(payment: Payment, success_url: str, cancel_url: str):
    """
    Створює Stripe Session для оплати позичених книг або штрафів
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Borrowing Payment {payment.type}",
                    },
                    'unit_amount': 1000,  # Вітається динамічно вираховувати суму наприклад 10$ -> 1000 cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )

        # Зберігаємо дані сесії у платіжній моделі
        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()
        return session

    except stripe.error.StripeError as e:
        # Логіка обробки помилок Stripe
        print(f"Stripe error: {e}")
        return None


def check_payment_status(payment: Payment):
    """
    Перевіряє статус платежу через Stripe API
    """
    if not payment.session_id:
        raise ValueError("Payment does not have a Stripe session ID.")

    session = stripe.checkout.Session.retrieve(payment.session_id)
    if session.payment_status == 'paid':
        payment.status = Payment.Status.PAID
        payment.save()
        return True
    return False


class PaymentSuccessView(APIView):
    """
    Перевіряє, чи платіж успішний
    """

    def get(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
            if check_payment_status(payment):
                return Response({"detail": "Payment successful."}, status=status.HTTP_200_OK)
            return Response({"detail": "Payment incomplete."}, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)


class PaymentCancelView(APIView):
    """
    Повертає повідомлення про те, що платіж скасовано
    """

    def get(self, request, pk):
        return Response({"detail": "Payment canceled."}, status=status.HTTP_200_OK)


class StartPaymentView(APIView):
    """
    Ініціює Stripe сесію для платежу
    """

    def post(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
            success_url = request.build_absolute_uri(reverse('payment-success', args=[payment.id]))
            cancel_url = request.build_absolute_uri(reverse('payment-cancel', args=[payment.id]))

            session = create_stripe_payment_session(payment, success_url, cancel_url)
            if session:
                return Response({"session_url": session.url}, status=status.HTTP_200_OK)
        except:
            raise Exception


# @api_view(["GET"])
# def create_test_payment(request):
#
#
#     try:
#         payment_intent = stripe.PaymentIntent.create(
#             amount=1000,
#             currency='usd',
#             payment_method_types=['card'],
#         )
#         return JsonResponse({'client_secret': payment_intent.client_secret})
#     except stripe.error.StripeError as e:
#         return JsonResponse({'error': str(e)}, status=400)

stripe.api_key = "sk_test_51QdBFIATMiqNcRwgnrmcwyZoU1kRZ952y1q0DPKGCXLgQ3KEqM6YC3JJbAuWCAwEAVpVNQ27bDtC6ne5rcSksKgO00jqFpX6s1"

@api_view(["GET"])
def create_checkout_session(request):
    borrowing = Borrowing.objects.all().first()

    payment = Payment(
        borrowing=borrowing,
        money_to_pay=10,
    )
    payment.save()

    payment = Payment.objects.get(id=payment.id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': payment.stripe_price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/success/',
        cancel_url='http://127.0.0.1:8000/cancel/',
    )
    return JsonResponse(
        {'session_id': session.id, "session_url": session.url},
    )
