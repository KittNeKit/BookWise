from decimal import Decimal

from datetime import timedelta
from typing import Any

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone

import stripe

from borrowings.models import Borrowing, Payment
from borrowings.notification import send_notification
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    PaymentSerializer,
    PaymentDetailSerializer,
)
from borrowings.stripe import create_stripe_session


@extend_schema_view(
    list=extend_schema(
        description=(
                "All borrowings in the library endpoint "
                "(User can see only own borrowings, "
                "admin can see all of them)."
        )
    ),
    retrieve=extend_schema(description="Specific borrowing endpoint."),
    create=extend_schema(description="Creating a new borrowing endpoint."),
)
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="For admins - filter by user_id (ex. '?user_id=1).",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="is_active",
                description="Filter by active borrowings (ex. ?is_active=True).",
                required=False,
                type=str,
            ),
        ],
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(self, request, *args, **kwargs)

    @action(detail=True, url_path="return", methods=["post"])
    def return_book(self, request, pk=None):
        """
        Returning book endpoint that closing the specific borrowing.
        """
        borrowing = Borrowing.objects.get(pk=pk)

        if borrowing.actual_return_date is None:  # check if book has not yet been returned
            borrowing.actual_return_date = timezone.now()
            borrowing.book_id.inventory += 1

            if borrowing.actual_return_date - borrowing.expected_return_date > timedelta(0):
                # check that borrowing have fine
                stripe_session = create_stripe_session(
                    borrowing=borrowing,
                    is_fine=True
                )
                Payment.objects.create(
                    status="PENDING",
                    type="FINE",
                    borrowing_id=borrowing,
                    session_url=stripe_session["url"],
                    session_id=stripe_session["id"],
                    to_pay=Decimal(stripe_session["amount_total"] / 100),
                )

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

    @action(
        methods=["GET"],
        detail=True,
        url_path="success",
    )
    def borrowing_is_successfully_paid(self, request, pk=None):
        """
        Success payment endpoint after paying for the borrowing
        """
        borrowing = self.get_object()
        session_id = request.query_params.get("session_id")
        payment = Payment.objects.get(session_id=session_id)
        session = stripe.checkout.Session.retrieve(session_id)

        if session["payment_status"] == "paid":
            payment.status = "PAID"
            payment.save()
            send_notification(f"{payment} was paid.")
            serializer = self.get_serializer(borrowing)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"Fail": "Payment wasn't successful."}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=["GET"],
        detail=True,
        url_path="cancel",
    )
    def borrowing_payment_is_cancelled(self, request, pk=None):
        """
        Cancel endpoint for borrowing payment.
        """
        borrowing = self.get_object()
        session_id = request.query_params.get("session_id")
        session = stripe.checkout.Session.retrieve(session_id)
        return Response(
            {
                "Cancel": f"The payment for the {borrowing} is cancelled. "
                          f"Make sure to pay during 24 hours. Payment url: "
                          f"{session.url}. Thanks!"
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(
        description=(
                "All payments endpoint "
                "(User can see only own payments, "
                "admin can see all of them)."
        )
    ),
    retrieve=extend_schema(description="Endpoint for getting a specific payment."),
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
                queryset = queryset.filter(borrowing_id__user_id=user_id)

            return queryset

        queryset = queryset.filter(borrowing_id__user_id=self.request.user.id)
        return queryset
