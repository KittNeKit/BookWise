from rest_framework import viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingDetailSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book_id", "user_id")
    serializer_class = BorrowingSerializer

    def get_queryset(self):
        return Borrowing.objects.filter(user_id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)
