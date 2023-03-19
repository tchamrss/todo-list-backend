from django.shortcuts import render
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from videoflix_app.serializers import VideoSerializer
from videoflix_app.models import Video
from rest_framework import authentication, permissions
from rest_framework.response import Response


from django.urls import reverse
from django.views import View
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
""" from todolist.serializers import TodoItemSerializer
from todolist.models import TodoItem """
from django.contrib.auth import get_user_model,authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
import json
from rest_framework import status
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
# Create your views here.
#@cache_page(CACHE_TTL)

""" from videoflix_app.admin import VideoResource
dataset = VideoResource().export()
dataset.json """

class VideoView(APIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Return a list of all todos.
        """
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)
    
    

# Create your views here.

""" class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        User = get_user_model()
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        uid = user.pk
        userObj = User.objects.get(pk=uid) 
        if not userObj.is_active:
            return JsonResponse({'error': 'Please activate your account'})           
        else:
            token, created = Token.objects.get_or_create(user=user)    
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }) """


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        if email is None or password is None:
            return Response({'error': 'Please provide both email and password'},
                            status=status.HTTP_400_BAD_REQUEST)
        User = get_user_model()
        userObj = User.objects.get(email=email)
        #print(userObj)
        print(userObj.username)
        user = authenticate(request=request, username=userObj.username, password=password)
        print(user)
        if user is None:
            return Response({'error': 'Invalid email/password'},
                            status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return JsonResponse({'error': 'Please activate your account'})
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })     

class LogoutView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
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

""" class TodoItemView(APIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        
        #Return a list of all todos.
        
        todos = TodoItem.objects.filter(author=request.user)
        serializer = TodoItemSerializer(todos, many=True)
        return Response(serializer.data) """
    

class UserRegistrationView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UserRegistrationView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        User = get_user_model()
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        if not username or not email or not password:
            return JsonResponse({'error': 'Please provide all the required fields'})
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'User with this email already exists.'})
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()
        token = Token.objects.create(user=user)
        send_confirmation_email(request, user, token)
        
        return JsonResponse({'message': 'Please check your email to activate your account'})
        #return JsonResponse({'token': token.key})
    
def send_confirmation_email(request, user, Token):
    print(Token)
    subject = 'Confirm your registration'
    message = render_to_string('auth/email_confirmation.html', {
        'user': user,
        'domain': request.META['HTTP_HOST'],
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': Token.key
    })
    print(message)
    from_email = 'russell.tchamba@gmail.com'
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)


def activate(request, uidb64, token):
    User = get_user_model()
    print(token)
    try:
        # Decode the user ID and token from the URL
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    print(uid)
    # Verify the token and activate the user
    if user is not None :
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login to your account.')
    else:
        return HttpResponse('Activation link is invalid or has expired.')