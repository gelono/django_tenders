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
from django.contrib.auth.views import LogoutView
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers, permissions

from django_tenders.views import session_auth
from tenders.auth_views import login_view, register_view, logout_view
from tenders.viewsets import ArchiveTenderViewSet, CustomerViewSet, WinnerViewSet, BalanceViewSet, TransactionInView, \
    ExtendedCompanyDataView, ActiveTenderViewSet

from rest_framework.authtoken import views

schema_view = get_schema_view(
   openapi.Info(
      title="Books API API",
      default_version='v1',
      contact=openapi.Contact(email="vitalii@vitalii.tech"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = routers.DefaultRouter()
router.register('archive_tenders', ArchiveTenderViewSet)
router.register('active_tenders', ActiveTenderViewSet)
router.register('customers', CustomerViewSet)
router.register('winners', WinnerViewSet)
router.register('balances', BalanceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # path('api-token-auth/', views.obtain_auth_token),
    # path('api-session-auth/', session_auth),
    path('api/login', login_view),
    path('api/register', register_view),
    path('api/logout', logout_view),
    path('transactions_in/', TransactionInView.as_view()),
    path('extended_company_data/', ExtendedCompanyDataView.as_view()),
    re_path(r'^api/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^api/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^api/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("", TemplateView.as_view(template_name="index.html")),
    path("accounts/", include("allauth.urls")),
    path("logout", LogoutView.as_view()),
]
