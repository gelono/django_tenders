from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from tenders.serializers import RegistrationSerializer


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def login_view(request):
    # request.data = {'username': 'admin', 'password': 'admin123'}
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    # Session-based authentication
    # if user is not None:
    #     login(request, user)
    #     return Response({'status': 'ok', 'user': user.username})
    # else:
    #     return Response({'status': 'error', 'message': 'Wrong username or password'}, status=400)

    # Token-based authentication
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    else:
        return Response({'status': 'error', 'message': 'Wrong username or password'}, status=400)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register_view(request):
    serializer = RegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        token = Token.objects.create(user=user)
        return Response({'status': 'ok', 'user': user.username, 'token': token.key})
    else:
        return Response({'status': 'error', 'message': serializer.errors}, status=400)


@api_view(['POST'])
def logout_view(request):
    # Token-based authentication
    request.user.auth_token.delete()
    return Response({'status': 'ok'})
