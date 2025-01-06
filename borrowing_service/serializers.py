from datetime import datetime, date

from django.db import transaction
from rest_framework import serializers

from accounts.serializers import UserSerializer
from books_service.serializers import BookDetailSerializer
from borrowing_service.models import Borrowing
from payments_service.models import Payment
from payments_service.serializers import PaymentSerializer


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(source="book.title", read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookDetailSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Borrowing.validate_borrowing(
            date.today(), attrs["expected_return_date"]
        )
        return data

    class Meta:
        model = Borrowing
        fields = ("id", "book", "payments", "expected_return_date")

    def create(self, validated_data):
        print(validated_data)
        with transaction.atomic():
            book = validated_data.get("book")
            if book.inventory == 0:
                raise serializers.ValidationError(
                    {f"{book.title}": "This book is out of stock now"}
                )
            book.inventory -= 1
            book.save()
            borrowing = Borrowing.objects.create(**validated_data)
        Payment.objects.create(borrowing=borrowing)
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField(
        default=datetime.now, read_only=True
    )

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
