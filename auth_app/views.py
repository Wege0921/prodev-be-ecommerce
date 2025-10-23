from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ResetPinSerializer

User = get_user_model()

class ResetPinView(APIView):
    authentication_classes = []  # unauthenticated for now (biometric is on-device)
    permission_classes = []      # add throttling/rate limit in production

    def post(self, request, *args, **kwargs):
        s = ResetPinSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        phone = s.validated_data['phone']
        new_pin = s.validated_data['new_pin']

        # Assuming username == phone
        user = User.objects.filter(username=phone).first()
        if not user:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_pin)
        user.save(update_fields=['password'])
        return Response(status=status.HTTP_204_NO_CONTENT)