from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer


@extend_schema_view(
    post=extend_schema(description="Creating user endpoint."),
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


@extend_schema_view(
    get=extend_schema(
        description="Detail info about current user endpoint."
    ),
    put=extend_schema(description="Updating the current user endpoint."),
    patch=extend_schema(
        description="Partially update the current user endpoint."
    ),
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
