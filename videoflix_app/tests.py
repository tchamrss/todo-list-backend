from unittest import signals
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Permission
from django.contrib.admin.sites import AdminSite
from videoflix_app.admin import VideoAdmin
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json
from datetime import date
from .models import Video
from .serializers import VideoSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
import os
import io
import sys
from django.dispatch import Signal
from .signals import video_post_save, video_post_delete
from django.apps import apps
from django.conf import settings
from videoflix_app.apps import VideoflixAppConfig


class UserRegistrationViewTestCase(TestCase):

    def setUp(self):
        self.url = '/register/'

    def test_valid_user_registration(self):
        data = {
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'test_password',
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Please check your email to activate your account'})

    def test_invalid_user_registration(self):
        data = {
            'username': '',
            'email': 'test@test.com',
            'password': 'test_password',
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        print(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Please provide all the required fields'})

class LogoutViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
    # Set the token in the request header
    def test_valid_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/logout/')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Logout erfolgreich"})
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_unauthorized_logout(self):
        response = self.client.post('/logout/')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})
        #self.assertEqual(response.data, {"error": "Benutzer nicht authentifiziert"})


class VideoSerializerTestCase(TestCase):
    def setUp(self):
        video_file = SimpleUploadedFile(
            name='test_video.mp4',
            content=open('media/videos/dog_8HLwTIo_480p.mp4', 'rb').read(),
            content_type='video/mp4'
        )
        self.video = Video.objects.create(
            title='Test Video',
            description='This is a test video',
            genres='Drama',
            playtime='01:30:00',
            picture=None,
            likes=10,
            created_at=timezone.now().date(),
            video_file=video_file
        )
        self.valid_payload = {
            'title': 'Test Video',
            'description': 'This is a test video',
            'genres': 'Drama',
            'playtime': '01:30:00',
            'picture': None,
            'likes': 100,
            'created_at': date.today().isoformat(),
            'video_file': self.video.video_file,
        }
        self.invalid_payload = {
            'title': '',
            'description': 'This is a test video',
            'genres': 'Action, Drama',
            'playtime': '01:30:00',
            'likes': 100,
            'created_at': date.today().isoformat(),
        }
        

    def tearDown(self):
        self.video.video_file.delete()

    def test_valid_serialization(self):
        serializer = VideoSerializer(instance=self.video)
        expected_data = {
            'id': self.video.id,  # add id field
            'title': 'Test Video',
            'description': 'This is a test video',
            'genres': 'Drama',
            'playtime': '01:30:00',
            'picture': None,
            'likes': 10,
            'created_at': self.video.created_at.isoformat(),  # convert to string
            'video_file': self.video.video_file.url,
        }
        self.assertEqual(serializer.data, expected_data)

    def test_invalid_serialization(self):
        serializer = VideoSerializer(data=self.invalid_payload)
        self.assertFalse(serializer.is_valid())

    def test_valid_deserialization(self):
        serializer = VideoSerializer(data=self.valid_payload)
        if not serializer.is_valid():
            print(serializer.errors)
        self.assertTrue(serializer.is_valid())
        video = serializer.save()
        self.assertEqual(video.title, 'Test Video')
        self.assertEqual(video.description, 'This is a test video')
        self.assertEqual(video.genres, 'Drama')
        self.assertEqual(video.playtime, '01:30:00')
        self.assertEqual(video.likes, 100)
        self.assertEqual(video.created_at, date.today())
        self.assertTrue(video.video_file)
        #self.assertEqual(video.video_file.name, 'videos/test_video_s3Vfdlh.mp4')

    def test_invalid_deserialization(self):
        serializer = VideoSerializer(data=self.invalid_payload)
        self.assertFalse(serializer.is_valid())

class VideoModelTestCase(TestCase):
    def setUp(self):
        video_file = SimpleUploadedFile(
            name='test_video.mp4',
            content=open('media/videos/dog_8HLwTIo_480p.mp4', 'rb').read(),
            content_type='video/mp4'
        )
        self.video = Video.objects.create(
            title='Test Video',
            description='This is a test video',
            genres='Drama',
            playtime='01:30:00',
            likes=10,
            created_at=date.today(),
            video_file=video_file
        )

    def test_video_str(self):
        self.assertEqual(str(self.video), 'Test Video')

    def test_video_fields(self):
        self.assertEqual(self.video.title, 'Test Video')
        self.assertEqual(self.video.description, 'This is a test video')
        self.assertEqual(self.video.genres, 'Drama')
        self.assertEqual(self.video.playtime, '01:30:00')
        self.assertEqual(self.video.likes, 10)
        self.assertEqual(self.video.created_at, date.today())
        
        
class AppConfigTestCase(TestCase):

    def test_default_auto_field(self):
        self.assertEqual(VideoflixAppConfig.default_auto_field, 'django.db.models.BigAutoField')


class VideoAdminTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='admin')
        self.user.set_password('test')
        self.user.user_permissions.add(Permission.objects.get(codename='add_video'))
        self.user.user_permissions.add(Permission.objects.get(codename='change_video'))
        self.user.user_permissions.add(Permission.objects.get(codename='delete_video'))
        self.user.is_staff = True
        self.user.save()
        self.test_video_file = SimpleUploadedFile(
            name='test_video.mp4',
            content=open('media/videos/dog_8HLwTIo_480p.mp4', 'rb').read(),
            content_type='video/mp4'
        )
        self.video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genres='Action',
            playtime='02:30:00',
            likes=0,
            created_at=timezone.now(),
            video_file=self.test_video_file
        )
        self.site = AdminSite()
        self.video_admin = VideoAdmin(Video, self.site)

    def test_video_admin_page_loads_successfully(self):
        request = self.factory.get('/admin/videoflix_app/video/')
        request.user = self.user
        response = self.video_admin.changelist_view(request)
        self.assertEqual(response.status_code, 200)

    def test_video_admin_add_new_video(self):
        data = {
            'title': 'Test Video',
            'description': 'Test video 2 description',
            'playtime': '00:20:00'
        }
        request = self.factory.post('/admin/videoflix_app/video/add/', data)
        request.user = self.user
        response = self.video_admin.add_view(request)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Video.objects.filter(title='Test Video').exists())

    def test_video_admin_delete_video(self):
        request = self.factory.post(f'/admin/videoflix_app/video/{self.video.pk}/delete/', {'post': 'yes'})
        request.user = self.user
        response = self.video_admin.delete_view(request, self.video.pk)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Video.objects.filter(pk=self.video.pk).exists())
       
        