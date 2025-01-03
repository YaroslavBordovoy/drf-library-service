# import stripe
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.urls import reverse
# from rest_framework.decorators import api_view
#
# from borrowing_service.models import Borrowing
# from .models import Payment
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.conf import settings
# from .models import Payment
#
#
# def check_payment_status(payment: Payment):
#     """
#     Перевіряє статус платежу через Stripe API
#     """
#     if not payment.session_id:
#         raise ValueError("Payment does not have a Stripe session ID.")
#
#     session = stripe.checkout.Session.retrieve(payment.session_id)
#     if session.payment_status == 'paid':
#         payment.status = Payment.Status.PAID
#         payment.save()
#         return True
#     return False
#
#
# class PaymentSuccessView(APIView):
#     """
#     Перевіряє, чи платіж успішний
#     """
#
#     def get(self, request, pk):
#         try:
#             payment = Payment.objects.get(pk=pk)
#             if check_payment_status(payment):
#                 return Response({"detail": "Payment successful."}, status=status.HTTP_200_OK)
#             return Response({"detail": "Payment incomplete."}, status=status.HTTP_400_BAD_REQUEST)
#         except Payment.DoesNotExist:
#             return Response({"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
#
#
# class PaymentCancelView(APIView):
#     """
#     Повертає повідомлення про те, що платіж скасовано
#     """
#
#     def get(self, request, pk):
#         return Response({"detail": "Payment canceled."}, status=status.HTTP_200_OK)
