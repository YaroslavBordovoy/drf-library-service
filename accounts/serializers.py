from django.contrib.auth import get_user_model
from packaging.utils import _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_staff",
        )
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "style": {"input_type": "password"},
                "label": _("Password"),
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def validate_email(self, value):
        if not "@" in value:
            raise serializers.ValidationError(
                "Please enter a valid email address."
            )

        return value

    def validate(self, attrs):
        first_name = attrs.get("first_name")
        last_name = attrs.get("last_name")

        if first_name is None or last_name is None:
            raise serializers.ValidationError(
                "Please provide your first name and last name."
            )

        if not first_name.isalpha() or not last_name.isalpha():
            raise serializers.ValidationError(
                "The first name and the last name must contain only letters."
            )

        return attrs
