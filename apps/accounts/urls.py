from django.urls import include, path

from . import views

urlpatterns = [
    path('plaid/token/get/', views.GetLinkTokenView.as_view(), name='create-link-token'),
    path('plaid/token/exchange/', views.ExchangePublicTokenView.as_view(), name='exchange-public-token'),
]
