from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing, Payment
from borrowings.serializers import BorrowingSerializer
from borrowings.tasks import check_overdue_borrowings
from library_project.settings import STRIPE_API_KEY

BORROWING_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id):
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


def sample_book(**params):
    defaults = {
        "title": "Harry Potter 2",
        "author": "J.K. Rowling",
        "cover": "Hard",
        "inventory": 5,
        "daily_fee": 0.5,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**params):
    defaults = {
        "borrow_date": "2023-01-01",
        "expected_return_date": "2023-01-04",
        "actual_return_date": "2023-12-12",
        "book_id": None,
        "user_id": None,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


def sample_setup(instance):
    instance.book = sample_book()
    instance.borrowing = sample_borrowing(book_id=instance.book, user_id=instance.user)

    instance.another_user = get_user_model().objects.create_user(
        "another_user@library.com", "password"
    )
    instance.borrowing_another_user = sample_borrowing(
        book_id=instance.book, user_id=instance.another_user
    )


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
            "authenticated@library.com", "password"
        )
        self.client.force_authenticate(self.user)
        sample_setup(self)

    def test_list_borrowings_display_this_user_borrowings(self):
        response = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.filter(user_id=self.user)
        serializer = BorrowingSerializer(borrowings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_borrowings_allowed(self):
        response = self.client.get(detail_url(self.user.borrowing.first().id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_another_user_borrowings_not_allowed(self):
        response = self.client.get(detail_url(self.another_user.borrowing.first().id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_borrowing_of_book_with_inventory_0(self):
        book = sample_book(title="Harry Potter 3", inventory=0)
        payload = {
            "expected_return_date": "2023-12-12",
            "actual_return_date": "2023-15-12",
            "book_id": book,
        }
        response = self.client.post(BORROWING_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_success_borrowing_and_decrease_inventory_by_1(self):
        start_inventory = self.book.inventory
        payload = {
            "expected_return_date": "2023-12-12",
            "book_id": self.book.id,
        }
        response = self.client.post(BORROWING_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Book.objects.get(pk=self.book.id).inventory, start_inventory - 1
        )

    def test_task_borrowings_overdue(self):
        with patch("requests.get") as mock_send_notification:
            check_overdue_borrowings()
            mock_send_notification.assert_called()

    def test_crate_payment_and_stripe_session_when_creating_a_borrowing(self):
        payload = {
            "expected_return_date": "2023-12-12",
            "book_id": self.book.id,
        }

        response = self.client.post(BORROWING_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payment = Payment.objects.last()
        self.assertEqual(payment.borrowing_id, Borrowing.objects.last())

        self.assertEqual(payment.status, "PENDING")
        self.assertEqual(payment.type, "PAYMENT")

        self.assertIsNotNone(payment.session_id)
        self.assertIsNotNone(payment.session_url)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "authenticated@library.com", "password"
        )
        self.client.force_authenticate(self.user)
        sample_setup(self)

    def test_filtering_by_user_id(self):
        another_borrowings = Borrowing.objects.filter(user_id__id=self.another_user.id)
        serializer_another = BorrowingSerializer(another_borrowings, many=True)

        response = self.client.get(BORROWING_URL, {"user_id": self.another_user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_another.data, response.data)
