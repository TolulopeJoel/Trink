from django.urls import path

from . import views

urlpatterns = [
    path('upload/receipt/', views.ExtractReceiptAPIView.as_view(), name='extract_receipt'),
]
