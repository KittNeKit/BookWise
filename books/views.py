from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from books.models import Book
from books.permissions import IsAdminOrIfUserReadOnly
from books.serializers import BooksSerializer


@extend_schema_view(
    list=extend_schema(description="All books endpoint in the library"),
    retrieve=extend_schema(description="Specific book endpoint in library"),
    create=extend_schema(description="Creating book endpoint"),
    update=extend_schema(description="Updating book endpoint"),
    partial_update=extend_schema(description="Partially update book endpoint"),
    destroy=extend_schema(description="Delete book endpoint"),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer
    permission_classes = (IsAdminOrIfUserReadOnly,)
    authentication_classes = (JWTAuthentication,)
