from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from videoflix_app.utils import activateUserandCreateToken, checkUserRegistration
from videoflix_app.serializers import VideoSerializer
from videoflix_app.models import Video
from rest_framework import authentication, permissions
from rest_framework.response import Response
from videoflix_app.utils import get_or_create_token, checkUser, get_user
from django.urls import reverse
from django.views import View
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model,authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
import json
import os
from rest_framework import status
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from  videoflix_app.tasks import convert_480p, convert_720p, convert_1080p


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
# Create your views here.
#@cache_page(CACHE_TTL)

class VideoView(APIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Return a list of all Videos.
        """
        print(Video.objects.latest)
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)
    
    
# Create your views here.
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Return the user informations when the validation is correct.
        """
        email = request.data.get("email")
        password = request.data.get("password")
        if email is None or password is None:
            return Response({'error': 'Please provide both email and password'},status=status.HTTP_400_BAD_REQUEST)
        user = get_user(email, password)
        response = checkUser(user)
        if response is not None:
            return response
        token = get_or_create_token(user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })



class LogoutView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        """
        log out the user and delete the token.
        """
        # Überprüfen Sie, ob der Benutzer authentifiziert ist und ein gültiges Token hat
        if request.auth:
            # Holen Sie sich das Token des Benutzers aus der Anfrage
            token = request.auth
            # Löschen Sie das Token des Benutzers
            token.delete()
            # Geben Sie eine Antwort zurück
            return Response({"message": "Logout erfolgreich"})
        else:
            # Wenn der Benutzer nicht authentifiziert ist oder kein gültiges Token hat, geben Sie eine Fehlermeldung zurück
            return Response({"error": "Benutzer nicht authentifiziert"}, status=status.HTTP_401_UNAUTHORIZED)
    

class UserRegistrationView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UserRegistrationView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """
        create a new user if not existing.
        """
        User = get_user_model()
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        response = checkUserRegistration(username, email, password, User)
        if response is not None:
            return response       
        user, token = activateUserandCreateToken(username, email, password, User)        
        send_confirmation_email(request, user, token)        
        return JsonResponse({'message': 'Please check your email to activate your account'})


    
def send_confirmation_email(request, user, Token):  
    """
        send the confirmation mail for activation.
    """  
    subject = 'Confirm your registration'
    message = render_to_string('auth/email_confirmation.html', {
        'user': user,
        'domain':request.META.get('HTTPS_HOST', settings.DOMAIN_NAME),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': Token.key
    })
    from_email = 'russell.tchamba@gmail.com'
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)


def activate(request, uidb64, token):
    """
        send an activation confirmation when clicking on the link in the email.
    """  
    User = get_user_model()
    try:
        # Decode the user ID and token from the URL
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # Verify the token and activate the user
    if user is not None :
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login to your account.')
    else:
        return HttpResponse('Activation link is invalid or has expired.')
