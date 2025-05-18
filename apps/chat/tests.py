from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.courses.models import Course

class CourseChatRoomViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.course = Course.objects.create(title='Test Course')
        self.course.students.add(self.user)
        self.course.save()

    def test_authenticated_user_can_access_own_course_chat_room(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('course_chat_room', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/room.html')
        self.assertContains(response, 'Test Course')

    def test_authenticated_user_cannot_access_not_joined_course(self):
        new_course = Course.objects.create(title='Another Course')
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('course_chat_room', args=[new_course.id]))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse('course_chat_room', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
