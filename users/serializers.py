from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.db import IntegrityError
import re

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "phone", "is_admin"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    # Validate uniqueness on phone at the API layer
    phone = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This phone is already registered.")]
    )
    # We’ll set username = normalized phone in validate(); keep it writable so DRF accepts it
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("username", "password", "password2", "phone")

    def validate_phone(self, raw: str) -> str:
        v = (raw or "").replace(" ", "")
        if v.startswith("+251"):
            v = v[4:]
        elif v.startswith("0"):
            v = v[1:]
        # 9 digits, starts with 9 or 7
        if not (len(v) == 9 and v and v[0] in ("9", "7") and v.isdigit()):
            raise serializers.ValidationError("Invalid phone format. Use +2519xxxxxxxx")
        # Return normalized E.164
        return f"+251{v}"

    def validate(self, attrs):
        pwd = attrs.get("password") or ""
        pwd2 = attrs.get("password2") or ""
        if pwd != pwd2:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Enforce 6-digit PIN to match the app
        if not re.fullmatch(r"\d{6}", pwd):
            raise serializers.ValidationError({"password": "PIN must be exactly 6 digits."})

        # username must equal normalized phone
        normalized_phone = attrs.get("phone")
        attrs["username"] = normalized_phone
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        username = validated_data.get("username")   # normalized phone
        phone = validated_data.get("phone")         # normalized phone

        user = User(**{**validated_data, "username": username})
        # Keep phone in sync if model has it
        if hasattr(user, "phone"):
            user.phone = phone

        user.set_password(password)
        try:
            user.save()
        except IntegrityError:
            # If DB unique constraint (username or phone) trips in a race condition, surface a clean 400
            raise serializers.ValidationError({"phone": "This phone is already registered."})
        return user




# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from django.contrib.auth.password_validation import validate_password

# User = get_user_model()

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["id", "username", "email", "first_name", "last_name", "phone", "is_admin"]

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = ("username", "password", "password2", "phone")

#     def validate(self, attrs):
#         if attrs["password"] != attrs["password2"]:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop("password2")
#         password = validated_data.pop("password")
#         phone = validated_data.pop("phone", "")
#         user = User(**validated_data)
#         if phone:
#             user.phone = phone
#         user.set_password(password)
#         user.save()
#         return user
