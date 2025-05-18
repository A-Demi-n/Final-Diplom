from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from apps.courses.models import Course, Subject


class ManageCourseListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='instructor', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')
        self.course1 = Course.objects.create(title='Course 1', owner=self.user)
        self.course2 = Course.objects.create(title='Course 2', owner=self.other_user)

        view_permission = Permission.objects.get(codename='view_course')
        self.user.user_permissions.add(view_permission)

    def test_course_list_only_shows_user_courses(self):
        self.client.login(username='instructor', password='pass')
        response = self.client.get(reverse('manage_course_list'))  # имя URL должно совпадать
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Course 1')
        self.assertNotContains(response, 'Course 2')

class CourseCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='pass')
        self.subject = Subject.objects.create(title='Math', slug='math')

        permission = Permission.objects.get(codename='add_course')
        self.user.user_permissions.add(permission)

    def test_create_course_success(self):
        self.client.login(username='creator', password='pass')
        response = self.client.post(reverse('course_create'), {
            'subject': self.subject.id,
            'title': 'New Course',
            'slug': 'new-course',
            'overview': 'Some overview'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(title='New Course').exists())

    def test_create_course_forbidden_without_permission(self):
        self.user.user_permissions.clear()
        self.client.login(username='creator', password='pass')
        response = self.client.get(reverse('course_create'))
        self.assertEqual(response.status_code, 403)


class CourseUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='editor', password='pass')
        self.subject = Subject.objects.create(title='Science', slug='science')
        self.course = Course.objects.create(
            title='Initial Title', slug='initial-title',
            overview='Initial overview', subject=self.subject,
            owner=self.user
        )
        permission = Permission.objects.get(codename='change_course')
        self.user.user_permissions.add(permission)

    def test_update_course_success(self):
        self.client.login(username='editor', password='pass')
        response = self.client.post(reverse('course_update', args=[self.course.id]), {
            'title': 'Updated Title',
            'slug': 'updated-title',
            'overview': 'Updated overview',
            'subject': self.subject.id
        })
        self.assertEqual(response.status_code, 302)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Title')

    def test_update_course_forbidden_if_not_owner(self):
        other_user = User.objects.create_user(username='hacker', password='hack')
        self.client.login(username='hacker', password='hack')
        response = self.client.post(reverse('course_update', args=[self.course.id]), {
            'title': 'Hack Title',
            'slug': 'hack-title',
            'overview': 'Oops',
            'subject': self.subject.id
        })
        self.assertEqual(response.status_code, 403)