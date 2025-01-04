from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from books_service.models import Book
from borrowing_service.models import Borrowing


class BorrowingModelTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="test_book",
            author="test_author",
            inventory=10,
            daily_fee=0.5
        )
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            first_name="test_first_name",
            last_name="test_last_name",
            password="testpassword"
        )

    def test_borrowing_str_(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date="2025-02-10"
        )

        self.assertEqual(
            str(borrowing),
            f"{self.book.title} "
            f"borrowed {borrowing.borrow_date} and "
            f"expected to return {borrowing.expected_return_date}"
        )

        borrowing.actual_return_date = "2025-01-10"

        self.assertEqual(
            str(borrowing),
            f"{self.book.title} "
            f"borrowed {borrowing.borrow_date} and "
            f"returned {borrowing.actual_return_date}"
        )

    def test_validate_borrowing(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date="2025-01-05",
            expected_return_date="2025-01-10"
        )

        self.assertIsNotNone(borrowing.id)

        with self.assertRaises(ValidationError):
            borrowing = Borrowing.objects.create(
                book=self.book,
                user=self.user,
                borrow_date="2025-01-05",
                expected_return_date="2025-01-01"
            )
