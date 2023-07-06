from django.db import models

from books.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateTimeField()
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField()
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
