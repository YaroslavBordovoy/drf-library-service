from django.test import TestCase
from .models import Book, Cover
from django.core.exceptions import ValidationError

from rest_framework.test import APITestCase
from .serializers import BookDetailSerializer


class BookModelTest(TestCase):
    def test_inventory_cannot_be_negative(self):
        book = Book(
            title="Book1",
            author="Author1",
            cover=Cover.HARD.name,
            inventory=-5,
            daily_fee=10.00,
        )
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_daily_fee_must_be_positive(self):
        book = Book(
            title="Book2",
            author="Author2",
            cover=Cover.SOFT.name,
            inventory=10,
            daily_fee=-1.00,
        )
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_valid_book(self):
        book = Book(
            title="Book3",
            author="Author3",
            cover=Cover.SOFT.name,
            inventory=10,
            daily_fee=5.00,
        )

        try:
            book.full_clean()
        except ValidationError:
            self.fail("Book model raised ValidationError")


class BookSerializerTest(APITestCase):
    def test_daily_fee_must_be_positive(self):
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "SOFT",
            "inventory": 10,
            "daily_fee": -5.00,
        }
        serializer = BookDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("daily_fee", serializer.errors)
        self.assertEqual(
            serializer.errors["daily_fee"][0],
            "Daily fee must be greater than 0.",
        )

    def test_valid_book_data(self):
        data = {
            "title": "Valid Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 5.00,
        }
        serializer = BookDetailSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, data)

    def test_author_with_valid_name(self):
        data = {
            "title": "Test Book",
            "author": "Steven King",
            "cover": "SOFT",
            "inventory": 10,
            "daily_fee": 5.00,
        }
        serializer = BookDetailSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_author_with_invalid_characters(self):
        data = {
            "title": "Test Book",
            "author": "Steven123 King",
            "cover": "SOFT",
            "inventory": 10,
            "daily_fee": 5.00,
        }
        serializer = BookDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("author", serializer.errors)
        self.assertEqual(
            serializer.errors["author"][0],
            "Author name must contain only letters and spaces.",
        )

    def test_author_with_special_characters(self):
        data = {
            "title": "Test Book",
            "author": "Steven! King",
            "cover": "SOFT",
            "inventory": 10,
            "daily_fee": 5.00,
        }
        serializer = BookDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("author", serializer.errors)
        self.assertEqual(
            serializer.errors["author"][0],
            "Author name must contain only letters and spaces.",
        )
