import json
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, URLPatternsTestCase

from .models import User, Course


class UserTest(APITestCase, URLPatternsTestCase):
    """ Authentication & Authorization Test cases """

    urlpatterns = [
        path('api/', include('api.urls')),
    ]

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='test1@test.com',
            password='Test@123',
        )

        self.admin = User.objects.create_superuser(
            email='admin@test.com',
            password='Admin@123'
        )
        

    def test_login(self):
        """ Testcase for user login and get a JWT response token """
        url = reverse('login')
        data = {
            'email': 'admin@test.com',
            'password': 'Admin@123'
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
            'password': 'Test@123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_all_users_as_admin(self):
        """ 
        Test fetching all users. Restricted to admins.
        It should return list of users 
        """
        
        url = reverse('login')
        data = {'email': 'admin@test.com', 'password': 'Admin@123'}
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
        data = {'email': 'test1@test.com', 'password': 'Test@123'}
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

    def test_add_course_as_admin(self):
        """ Testcase for adding a course as admin """
        url = reverse('login')
        data = {'email': 'admin@test.com', 'password': 'Admin@123'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)

        course_data = {'name': 'New Course', 'credit_hours': 3}
        response = client.post(reverse('course-list'), course_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.filter(name='New Course').count(), 1)
    
    def test_update_course_as_admin(self):
        """ Testcase for updating a course as admin """
        url = reverse('login')
        data = {'email': 'admin@test.com', 'password': 'Admin@123'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)

        # Create a course
        course_data = {'name': 'New Course', 'credit_hours': 3}
        response = client.post(reverse('course-list'), course_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = response.data['course']['id']

        # Update the course
        updated_course_data = {'name': 'Updated Course', 'credit_hours': 4}
        response = client.put(reverse('course-detail', args=[course_id]), updated_course_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Course.objects.get(id=course_id).name, 'Updated Course')

    def test_delete_course_as_admin(self):
        """ Testcase for deleting a course as admin """
        url = reverse('login')
        data = {'email': 'admin@test.com', 'password': 'Admin@123'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)

        # Create a course
        course_data = {'name': 'Course to Delete', 'credit_hours': 3}
        response = client.post(reverse('course-list'), course_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = response.data['course']['id']

        # Delete the course
        response = client.delete(reverse('course-detail', args=[course_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=course_id).exists())

    def test_view_courses_as_admin(self):
        """ Testcase for viewing all courses as admin """
        url = reverse('login')
        data = {'email': 'admin@test.com', 'password': 'Admin@123'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)

        # Create some courses
        Course.objects.create(name='Course 1', credit_hours=3)
        Course.objects.create(name='Course 2', credit_hours=4)

        # Fetch all courses
        response = client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['courses']), Course.objects.count())

    def test_student_register_course(self):
        """
        Test case for registering course
        """
        # Login admin to create courses
        url = reverse('login')
        admin_data = {'email': 'admin@test.com', 'password': 'Admin@123'}
        response = self.client.post(url, admin_data)
        admin_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in admin_response_data)
        admin_token = admin_response_data['access']

        # Create a course
        url_create_course = reverse('course-list')
        client_admin = APIClient()
        client_admin.credentials(HTTP_AUTHORIZATION='JWT ' + admin_token)
        course_data = {'name': 'New Course', 'credit_hours': 3}
        response_create_course = client_admin.post(url_create_course, course_data)
        self.assertEqual(response_create_course.status_code, status.HTTP_201_CREATED)

        # Login as student
        url_login = reverse('login')
        student_data = {'email': 'test1@test.com', 'password': 'Test@123'}
        response_login = self.client.post(url_login, student_data)
        login_response_data = json.loads(response_login.content)
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        student_token = login_response_data['access']

        # Student registers for the newly created course
        url_register = reverse('registered-courses-list')
        data_register = {'course': Course.objects.last().id, 'user': self.user1.id}
        client_student = APIClient()
        client_student.credentials(HTTP_AUTHORIZATION='JWT ' + student_token)
        response_register = client_student.post(url_register, data_register)
        self.assertEqual(response_register.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user1.courses.count(), 1)
    
    def test_student_register_course_max_credit_hours(self):
        # Login admin to create courses
        url = reverse('login')
        admin_data = {'email': 'admin@test.com', 'password': 'Admin@123'}
        response = self.client.post(url, admin_data)
        admin_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in admin_response_data)
        admin_token = admin_response_data['access']

        # Create courses
        url_create_course = reverse('course-list')
        client_admin = APIClient()
        client_admin.credentials(HTTP_AUTHORIZATION='JWT ' + admin_token)

        # Create courses with different credit hours
        course_data_1 = {'name': 'Course 1', 'credit_hours': 5}
        course_data_2 = {'name': 'Course 2', 'credit_hours': 7}
        client_admin.post(url_create_course, course_data_1)
        client_admin.post(url_create_course, course_data_2)

        # Login as student
        url_login = reverse('login')
        student_data = {'email': 'test1@test.com', 'password': 'Test@123'}
        response_login = self.client.post(url_login, student_data)
        login_response_data = json.loads(response_login.content)
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        student_token = login_response_data['access']

        # Student registers for courses
        url_register = reverse('registered-courses-list')
        data_register_1 = {'course': Course.objects.get(name='Course 1').id, 'user': self.user1.id}
        data_register_2 = {'course': Course.objects.get(name='Course 2').id, 'user': self.user1.id}
        
        client_student = APIClient()
        client_student.credentials(HTTP_AUTHORIZATION='JWT ' + student_token)
        response_register_1 = client_student.post(url_register, data_register_1)
        response_register_2 = client_student.post(url_register, data_register_2)

        # Check if registration is successful
        self.assertEqual(response_register_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_register_2.status_code, status.HTTP_201_CREATED)

        # Check if the student's total credit hours do not exceed the maximum
        self.assertEqual(self.user1.get_credit_hours(), 12)
