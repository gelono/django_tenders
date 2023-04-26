from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request


class AdminSecretHeaderAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        secret_header = request.META.get("HTTP_SECRET_HEADER")
        if secret_header is None:
            return None

        if secret_header == 'qwerty123':
            try:
                user = User.objects.get(email='gelonooz@gmail.com')
            except ObjectDoesNotExist as e:
                print(e)
                return None
            else:
                return user, None
