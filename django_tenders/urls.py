"""django_tenders URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from django_tenders.views import session_auth
from tenders.viewsets import ArchiveTenderViewSet, CustomerViewSet, WinnerViewSet, BalanceViewSet, TransactionInView, \
    ExtendedCompanyDataView

from rest_framework.authtoken import views

router = routers.DefaultRouter()
router.register('archive_tenders', ArchiveTenderViewSet)
router.register('customers', CustomerViewSet)
router.register('winners', WinnerViewSet)
router.register('balances', BalanceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-session-auth/', session_auth),
    path('transactions_in/', TransactionInView.as_view()),
    path('extended_company_data/', ExtendedCompanyDataView.as_view()),
]
