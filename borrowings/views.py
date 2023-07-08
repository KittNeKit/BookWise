from datetime import datetime

from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from borrowings.models import Borrowing, Payment
from borrowings.serializers import BorrowingSerializer, BorrowingDetailSerializer, PaymentSerializer, \
    PaymentDetailSerializer


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Borrowing.objects.select_related("book_id", "user_id")
    serializer_class = BorrowingSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_staff == 1:
            user_id = self.request.query_params.get("user_id")

            if user_id:
                queryset = queryset.filter(user_id=user_id)

            return queryset

        queryset = queryset.filter(user_id=self.request.user.id)
        is_active = self.request.query_params.get("is_active")

        if is_active == "1":
            queryset = queryset.filter(actual_return_date__isnull=True)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

    @action(detail=True, url_path="return", methods=["post"])
    def return_book(self, request, pk=None):
        borrowing = Borrowing.objects.get(pk=pk)

        if borrowing.actual_return_date is None:
            borrowing.actual_return_date = datetime.now()
            borrowing.book_id.inventory += 1
            borrowing.book_id.save()
            borrowing.save()
            return Response(
                {'success': 'You are return your borrowing book.'},
                status.HTTP_200_OK
            )

        return Response(
            {'error': 'You can not return already returned book.'},
            status.HTTP_403_FORBIDDEN
        )


class PaymentViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer

        return PaymentSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_staff == 1:
            user_id = self.request.query_params.get("user_id")

            if user_id:
                queryset = queryset.filter(user_id=user_id)

            return queryset

        queryset = queryset.filter(borrowing_id__user_id=self.request.user.id)

        return queryset
