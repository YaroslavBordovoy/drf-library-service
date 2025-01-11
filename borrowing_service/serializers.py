from datetime import datetime, date

from django.db import transaction
from rest_framework import serializers

from accounts.serializers import UserSerializer
from books_service.serializers import BookDetailSerializer, BookSerializer
from borrowing_service.models import Borrowing
from notifications_service.notifications import notify_booking_created, notify_payment_needed
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
            payment = Payment.objects.create(borrowing=borrowing)

            notify_booking_created(
                user_id=borrowing.user.id,
                book_title=borrowing.book.title,
                borrow_date=borrowing.borrow_date,
                expected_return_date=borrowing.expected_return_date
            )
            if payment.session_url:
                notify_payment_needed(
                    user_id=borrowing.user.id,
                    book_title=borrowing.book.title,
                    payment_url=payment.session_url
                )


        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField(
        default=datetime.now, read_only=True
    )

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")


class BorrowingSuccessSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = Borrowing
        fields = ["id", "book", "expected_return_date", "borrow_date"]
