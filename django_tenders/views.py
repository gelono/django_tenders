from django.contrib.auth import authenticate, login
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(http_method_names=["POST"])
@authentication_classes([])
@permission_classes([])
def session_auth(request: Request):
    data = request.data
    user = authenticate(username=data["username"], password=data["password"])

    if user:
        login(request, user)
        return Response(user.username)
    else:
        return Response("Unauthorized", status=401)
