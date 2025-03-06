from rest_framework import status, permissions, viewsets, routers
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserRegistrationSerializer, UserPublicSerializer, ObtainTokenSerializer
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from users.service import Activator 


from .serializers import (
    UserRegistrationSerializer,
    UserPublicSerializer,
    UserActivationSerializer,
)

class UserAPIViewSet(viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return [permissions.AllowAny()]
        elif self.action is None:
            return [permissions.AllowAny()]
        elif self.action == "activate":
            return [permissions.AllowAny()]
        else:
            raise NotImplementedError(f"Action {self.action} is not ready yet")

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        service = Activator(email=getattr(serializer.instance, "email"))
        activation_key = service.create_activation_key()
        service.save_activation_information(
            user_id=getattr(serializer.instance, "id"), activation_key=activation_key
        )
        service.send_user_activation_email(activation_key=activation_key)

        # actional_key: uuid.UUID = service.create_activation_key(
        #     email=serializer.validated_data["email"]
        # )
        # service.send_user_activation_email(
        #     email=serializer.validated_data["email"], actional_key=actional_key
        # )

        return Response(
            UserPublicSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    def list(self, request):
        return Response(
            UserPublicSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )
    
    @action(methods=["POST"], detail=False)
    def activate(self, request):
        serializer = UserActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = Activator()
        service.activate_user(activation_key=serializer.validated_data.get("key"))

        # serializer.validated_data
        return Response(data=None, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def token(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh_token = str(RefreshToken.for_user(user))
        access_token = str(RefreshToken.for_user(user).access_token)
        
        return Response({'access': access_token,'refresh': refresh_token,}, status=status.HTTP_200_OK)
        

router = routers.DefaultRouter()
router.register(r"users", UserAPIViewSet, basename="user")