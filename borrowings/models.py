from django.db import models

from books.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    book_id = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowing"
    )
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="borrowing"
    )


class Payment(models.Model):
    class StatusChoice(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeStatus(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(max_length=50, choices=StatusChoice.choices)
    type = models.CharField(max_length=50, choices=TypeStatus.choices)
    borrowing_id = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.CharField(max_length=500, null=True, blank=True)
    session_id = models.CharField(max_length=500, null=True, blank=True)
    to_pay = models.DecimalField(decimal_places=2, max_digits=10)
