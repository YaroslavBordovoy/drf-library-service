from unittest import TestCase
from unittest.mock import patch

from django.contrib.auth import get_user_model

from books_service.models import Book
from borrowing_service.models import Borrowing
from payments_service.models import Payment, calculate_sum


class PaymentModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="new_test_user@test.com",
            password="testpassword",
        )
        self.book = Book.objects.create(
            title="Test_Book",
            author="Test Author",
            inventory=10,
            daily_fee=1.5,
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date="2025-01-10",
            expected_return_date="2025-01-20",
        )

    @patch("payments_service.models.get_stripe_data")
    def test_payment_session_creation(self, mock_get_stripe_data):
        mock_get_stripe_data.return_value = (
            "session_id_example",
            "http://example.com/checkout/session_url",
        )

        payment = Payment.objects.create(
            borrowing=self.borrowing,
            money_to_pay=22.5,
        )

        self.assertEqual(payment.session_id, "session_id_example")
        self.assertEqual(
            payment.session_url,
            "http://example.com/checkout/session_url",
        )

        mock_get_stripe_data.assert_called_once_with(
            money_to_pay=22.5,
            title="Test_Book",
            borrowing_id=self.borrowing.id,
        )

    def tearDown(self):
        get_user_model().objects.all().delete()
        Book.objects.all().delete()
        Borrowing.objects.all().delete()
