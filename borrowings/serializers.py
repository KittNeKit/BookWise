from django.db import transaction
from rest_framework import serializers

from books.serializers import BooksSerializer
from borrowings.models import Borrowing


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
        return Borrowing.objects.create(**validated_data)


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
