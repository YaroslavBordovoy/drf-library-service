from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from borrowing_service.models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(
        source="book_service.book.title", read_only=True
    )
    user = serializers.CharField(
        source="accounts.user.email", read_only=True
    )

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
    # book = BookDetailSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Borrowing.validate_borrowing(
            attrs["borrow_date"], attrs["expected_return_date"]
        )
        return data

    class Meta:
        model = Borrowing
        fields = ("id", "book", "expected_return_date")

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data.get("book")
            if book.inventory == 0:
                raise serializers.ValidationError(
                    {"book": "This book is out of stock now"}
                )
            book.inventory -= 1
            book.save()
            borrowing = Borrowing.objects.create(**validated_data)
            return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField(
        default=datetime.now, read_only=True
    )

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
