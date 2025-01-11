from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books_service.models import Book
from borrowing_service.models import Borrowing
from borrowing_service.serializers import BorrowingListSerializer, BorrowingDetailSerializer


BORROWING_URL = reverse("borrowing:borrowing-list")


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
            Borrowing.objects.create(
                book=self.book,
                user=self.user,
                borrow_date="2025-01-05",
                expected_return_date="2025-01-01"
            )

    def tearDown(self):
        get_user_model().objects.all().delete()

class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            first_name="testfirstname",
            last_name="testlastname",
            email="testemail@test.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)
        self.book_1 = Book.objects.create(
            title="test_book",
            author="test_author",
            inventory=10,
            daily_fee=0.5
        )
        self.book_2 = Book.objects.create(
            title="test_book_2",
            author="test_author_2",
            inventory=10,
            daily_fee=0.5
        )
        self.borrowing_1 = Borrowing.objects.create(
            book=self.book_1,
            user=self.user,
            expected_return_date="2025-02-10"
        )
        self.borrowing_2 = Borrowing.objects.create(
            book=self.book_2,
            user=self.user,
            expected_return_date="2025-02-15"
        )

    def test_auth_required(self):
        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_borrowing_list(self):
        response = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all().order_by("id")
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(response.data["results"], serializer.data)
        self.assertEqual(Borrowing.objects.count(), 2)

    def test_get_borrowing_detail(self):
        borrowing_detail_url = reverse(
            "borrowing:borrowing-detail",
            args=[self.borrowing_1.id]
        )
        response = self.client.get(borrowing_detail_url)

        borrowing = Borrowing.objects.get(pk=self.borrowing_1.id)
        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(response.data, serializer.data)

    def test_create_borrowing(self):
        data = {
            "book": self.book_1.id,
            "user": self.user.id,
            "expected_return_date": "2025-03-01"
        }
        initial_inventory = self.book_1.inventory
        response = self.client.post(BORROWING_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 3)
        self.assertEqual(Borrowing.objects.latest("id").user, self.user)

        self.book_1.refresh_from_db()

        self.assertEqual(self.book_1.inventory, initial_inventory - 1)

    def test_return_book_success(self):
        return_url = reverse(
            "borrowing:borrowing-return",
            args=[self.borrowing_1.id]
        )
        initial_inventory = self.book_1.inventory
        response = self.client.post(return_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"],
            f"{self.book_1.title} successfully returned!",
        )

        self.book_1.refresh_from_db()
        self.borrowing_1.refresh_from_db()

        self.assertEqual(self.book_1.inventory, initial_inventory + 1)
        self.assertEqual(self.borrowing_1.actual_return_date, date.today())

    def test_filter_is_active(self):
        response = self.client.get(BORROWING_URL, {"is_active": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["id"], self.borrowing_1.id)

    def test_filter_user_id(self):
        response = self.client.get(BORROWING_URL, {"user_id": self.user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
