from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "password",
        ]

    def validate(self, attrs: dict) -> dict:
        attrs["password"] = make_password(attrs["password"])
        return attrs


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "phone_number", "first_name", "last_name", "role"]


class UserActivationSerializer(serializers.Serializer):
    key = serializers.UUIDField()


class ObtainTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        user = User.objects.get(email=email)

        user = User.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError({"User doesn't exist"})
        if not user.is_active:
            raise serializers.ValidationError({"Usser isn't activated"})
        
        attrs['user'] = user
        return attrs
        