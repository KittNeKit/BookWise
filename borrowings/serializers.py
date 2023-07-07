from django.db import transaction
from rest_framework import serializers

from books.serializers import BooksSerializer
from borrowings.models import Borrowing
from borrowings.notification import send_borrowing_create_message


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

        send_borrowing_create_message(
            user=validated_data["user_id"],
            borrowing=borrowing
        )

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
