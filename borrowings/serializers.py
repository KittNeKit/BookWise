from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from books.serializers import BooksSerializer
from borrowings.models import Borrowing, Payment
from borrowings.notification import send_borrowing_create_message
from borrowings.stripe import create_stripe_session


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
        )

    @transaction.atomic()
    def create(self, validated_data):
        validated_data["book_id"].inventory -= 1
        validated_data["book_id"].save()

        borrowing = Borrowing.objects.create(**validated_data)

        stripe_session = create_stripe_session(
            borrowing=borrowing,
            is_fine=False
        )

        Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing_id=borrowing,
            session_url=stripe_session["url"],
            session_id=stripe_session["id"],
            to_pay=Decimal(stripe_session["amount_total"] / 100),
        )

        send_borrowing_create_message(
            user=validated_data["user_id"],
            borrowing=borrowing
        )
        print(stripe_session["payment_status"])
        return borrowing


class BorrowingDetailSerializer(BorrowingSerializer):
    book_id = BooksSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
            "user_id",
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing_id",
            "session_url",
            "session_id",
            "to_pay",
        )


class PaymentDetailSerializer(PaymentSerializer):
    borrowing_id = BorrowingDetailSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing_id",
            "session_url",
            "session_id",
            "to_pay",
        )
