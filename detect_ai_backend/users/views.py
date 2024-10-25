from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, response, status

from detect_ai_backend.users.models import User
from detect_ai_backend.users.serializers import (
    RegistrationSerializer,
    UserSerializer,
    UserUpdateResponseSerializer,
)


class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return response.Response(
                {"Message": "User created successfully", "User": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        return self.queryset.get(id=self.request.user.pk)

    @swagger_auto_schema(responses={status.HTTP_200_OK: UserUpdateResponseSerializer})
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: UserUpdateResponseSerializer})
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
