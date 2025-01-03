from rest_framework import serializers
from .models import Book


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author")


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")

    def validate_author(self, value):
        if not value.isalpha():
            raise serializers.ValidationError(
                "Author name must contain only letters."
            )
        return value

    def validate_inventory(self, value):
        if value < 0:
            raise serializers.ValidationError("Inventory cannot be negative.")
        return value

    def validate_daily_fee(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Daily fee must be greater than 0."
            )
        return value
