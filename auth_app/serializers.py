from rest_framework import serializers

class ResetPinSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    new_pin = serializers.RegexField(
        regex=r'^\d{6}$',
        error_messages={'invalid': 'PIN must be exactly 6 digits.'}
    )

    def validate_phone(self, value):
        if not value.startswith('+251'):
            raise serializers.ValidationError('Phone must be E.164, e.g. +2519xxxxxxx')
        return value


class GoogleAuthInSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class GoogleAuthOutSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.DictField()