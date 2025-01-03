from rest_framework import serializers
from .models import Book
import re


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author")

    def validate_author(self, value):
        if not all(part.isalpha() for part in value.split()):
            raise serializers.ValidationError(
                "Author name must contain only letters and spaces."
            )
        return value


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")

    def validate_author(self, value):
        if not all(part.isalpha() for part in value.split()):
            raise serializers.ValidationError(
                "Author name must contain only letters and spaces."
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
