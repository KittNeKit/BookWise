from rest_framework import routers

from borrowings.views import BorrowingViewSet, PaymentViewSet

app_name = "borrowings"

router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet)
router.register("payments", PaymentViewSet)

urlpatterns = [] + router.urls
