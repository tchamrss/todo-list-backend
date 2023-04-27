
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model,authenticate
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

def get_user(email, password):
    User = get_user_model()
    if not User.objects.filter(email=email).exists():
        return None
    user_obj = User.objects.get(email=email)
    user = authenticate(username=user_obj.username, password=password)
    return user

def get_or_create_token(user):
    token, created = Token.objects.get_or_create(user=user)
    return token

def checkUser(user):
    if user is None:
        return Response({'error': 'Incorrect email or password. Please try again.'},
                        status=status.HTTP_400_BAD_REQUEST)
    if not user.is_active:
        return Response({'error': 'Please activate your account.'},
                        status=status.HTTP_400_BAD_REQUEST)
    return None

def activateUserandCreateToken(username, email, password, User):
    user = User.objects.create_user(username=username, email=email, password=password)
    user.is_active = False
    user.save()
    token = Token.objects.create(user=user)
    return user, token

def checkUserRegistration(username, email, password, User):
    if not username or not email or not password:
            return JsonResponse({'error': 'Please provide all the required fields'},
                            status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'User with this email already exists.'},
                            status=status.HTTP_400_BAD_REQUEST)
    return None