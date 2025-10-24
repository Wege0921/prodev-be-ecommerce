from django.urls import path
from .views import ResetPinView, GoogleAuthView

urlpatterns = [
    path('reset-pin/', ResetPinView.as_view(), name='reset-pin'),
    path('google/', GoogleAuthView.as_view(), name='google-auth'),
]