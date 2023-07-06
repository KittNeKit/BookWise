from rest_framework import viewsets

from books.models import Book
from books.permissions import IsAdminOrIfUserReadOnly
from books.serializers import BooksSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer
    permission_classes = (IsAdminOrIfUserReadOnly,)
