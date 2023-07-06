from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from books.models import Book
from books.permissions import IsAdminOrIfUserReadOnly
from books.serializers import BooksSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer
    permission_classes = (IsAdminOrIfUserReadOnly,)
    authentication_classes = (JWTAuthentication,)
