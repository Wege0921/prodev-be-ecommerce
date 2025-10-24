from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ResetPinSerializer
import os
import requests
from rest_framework_simplejwt.tokens import RefreshToken

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


class GoogleAuthView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        id_token = request.data.get('id_token')
        if not id_token:
            return Response({'detail': 'id_token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            r = requests.get('https://oauth2.googleapis.com/tokeninfo', params={'id_token': id_token}, timeout=6)
        except Exception:
            return Response({'detail': 'Failed to validate token'}, status=status.HTTP_400_BAD_REQUEST)

        if r.status_code != 200:
            return Response({'detail': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)

        data = r.json()
        aud = data.get('aud')
        email = data.get('email')
        email_verified = str(data.get('email_verified', '')).lower() in {'1', 'true', 'yes'}
        name = data.get('name') or ''

        # Validate audience (client id)
        allowed_aud = {x.strip() for x in [
            os.getenv('GOOGLE_CLIENT_ID_ANDROID', ''),
            os.getenv('GOOGLE_CLIENT_ID_IOS', ''),
            os.getenv('GOOGLE_CLIENT_ID_WEB', ''),
        ] if x.strip()}
        if allowed_aud and aud not in allowed_aud:
            return Response({'detail': 'Token audience mismatch'}, status=status.HTTP_400_BAD_REQUEST)

        if not email or not email_verified:
            return Response({'detail': 'Email not verified'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        user = User.objects.filter(email=email).first()
        if not user:
            username = email
            user = User.objects.create_user(username=username, email=email)
            user.set_unusable_password()
            # optionally split name
            try:
                parts = name.split(' ')
                if not user.first_name and parts:
                    user.first_name = parts[0]
                if not user.last_name and len(parts) > 1:
                    user.last_name = ' '.join(parts[1:])
                user.save()
            except Exception:
                pass

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_200_OK)