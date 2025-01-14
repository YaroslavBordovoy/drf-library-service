from django.contrib.auth import get_user_model
from django.test import TestCase
from books_service.models import Book, Cover
from django.core.exceptions import ValidationError

from rest_framework.test import APITestCase, APIClient
from books_service.serializers import BookDetailSerializer
from rest_framework import status
from django.urls import reverse


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


class BookCreateViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.admin_user)

        self.url = reverse("book:book-create")

    def test_create_book_as_admin(self):
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": 10.00,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])

    def test_create_book_forbidden_for_non_admin(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpassword",
            is_staff=False
        )
        self.client.force_authenticate(self.user)

        data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": 10.00,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BookListViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Cover.SOFT.name,
            inventory=10,
            daily_fee=5.00,
        )
        self.url = reverse("book:book-list")

    def test_get_books(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], self.book.title)


class BookDetailViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Cover.SOFT.name,
            inventory=10,
            daily_fee=5.00,
        )
        self.url = reverse("book:book-detail", args=[self.book.pk])

    def test_get_book_detail(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.book.title)


class BookUpdateViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpassword",
            is_staff=False
        )
        self.client.force_authenticate(self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Cover.SOFT.name,
            inventory=10,
            daily_fee=5.00,
        )
        self.url = reverse("book:book-update", args=[self.book.pk])

    def test_update_book_forbidden(self):
        data = {
            "title": "Updated Test Book",
            "author": "Updated Author",
            "cover": "HARD",
            "inventory": 15,
            "daily_fee": 12.00,
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_as_admin(self):
        self.admin_user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.admin_user)

        data = {
            "title": "Updated Test Book",
            "author": "Updated Author",
            "cover": "HARD",
            "inventory": 15,
            "daily_fee": 12.00,
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], data["title"])


class BookDeleteViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.admin_user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Cover.SOFT.name,
            inventory=10,
            daily_fee=5.00,
        )
        self.url = reverse("book:book-delete", args=[self.book.pk])

    def test_delete_book_as_admin(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

    def test_delete_book_forbidden_for_non_admin(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpassword",
            is_staff=False
        )
        self.client.force_authenticate(self.user)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BookPermissionTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("book:book-list")

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Cover.SOFT.name,
            inventory=10,
            daily_fee=5.00,
        )

    def test_list_books_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], self.book.title)