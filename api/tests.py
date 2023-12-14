import json
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, URLPatternsTestCase

from .models import User


class UserTest(APITestCase, URLPatternsTestCase):
    """ Authentication & Authorization Test cases """

    urlpatterns = [
        path('api/auth/', include('api.urls')),
    ]

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='test1@test.com',
            password='test',
        )

        self.admin = User.objects.create_superuser(
            email='admin@test.com',
            password='admin',
        )

    def test_login(self):
        """ Testcase for user login and get a JWT response token """
        url = reverse('login')
        data = {
            'email': 'admin@test.com',
            'password': 'admin'
        }
        response = self.client.post(url, data)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['success'], True)
        self.assertTrue('access' in response_data)

    def test_user_registration(self):
        """ Testcase for user registration  """
        url = reverse('register')
        data = {
            'email': 'test2@test.com',
            'password': 'test',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_all_users_as_admin(self):
        """ 
        Test fetching all users. Restricted to admins.
        It should return list of users 
        """
        
        url = reverse('login')
        data = {'email': 'admin@test.com', 'password': 'admin'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = client.get(reverse('users'))
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), len(response_data['users']))

    def test_access_denied_all_users(self):
        """ Testcase for fetching all users. Restricted to admins only. It should be forbidden"""

        # Token setup
        url = reverse('login')
        data = {'email': 'test1@test.com', 'password': 'test'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        # Endpoint testing
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = client.get(reverse('users'))
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response_data['success'])
