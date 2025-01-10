from rest_framework import serializers

from books_service.models import Book
from borrowing_service.models import Borrowing
from payments_service.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("session_url", "session_id")


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["title", "author", "inventory", "daily_fee"]


class BorrowingSuccessSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = Borrowing
        fields = ["book", "expected_return_date", "borrow_date"]
