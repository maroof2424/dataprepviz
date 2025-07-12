from django.urls import path
from .views import FileUploadAPIView

urlpatterns = [
    path('api/upload/', FileUploadAPIView.as_view(), name='api_upload'),
]
