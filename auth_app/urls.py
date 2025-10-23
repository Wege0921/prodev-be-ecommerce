from django.urls import path
from .views import ResetPinView

urlpatterns = [
    path('reset-pin/', ResetPinView.as_view(), name='reset-pin'),
]