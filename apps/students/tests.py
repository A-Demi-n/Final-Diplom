from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.courses.models import Subject, Course, Module

class StudentRegistrationViewTest(TestCase):
    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(reverse('student_register'), {
            'username': 'student1',
            'password1': 'Testpass123!',
            'password2': 'Testpass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('student_course_list'))

        user = User.objects.get(username='student1')
        self.assertTrue(user.is_authenticated)


class StudentEnrollCourseViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student2', password='pass')
        self.subject = Subject.objects.create(title='Math', slug='math')
        self.course = Course.objects.create(title='Algebra', subject=self.subject, slug='algebra', owner=self.user)

    def test_enroll_student_in_course(self):
        self.client.login(username='student2', password='pass')
        response = self.client.post(reverse('student_enroll'), {
            'course': self.course.id
        })
        self.assertRedirects(response, reverse('student_course_detail', args=[self.course.id]))
        self.assertIn(self.user, self.course.students.all())


class StudentCourseListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student3', password='pass')
        self.subject = Subject.objects.create(title='Physics', slug='physics')
        self.course = Course.objects.create(title='Mechanics', subject=self.subject, slug='mech', owner=self.user)
        self.course.students.add(self.user)
    def test_course_list_for_enrolled_student(self):
        self.client.login(username='student3', password='pass')
        response = self.client.get(reverse('student_course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mechanics')

class StudentCourseDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student4', password='pass')
        self.subject = Subject.objects.create(title='Chemistry', slug='chemistry')
        self.course = Course.objects.create(title='Organic Chemistry', subject=self.subject, slug='orgchem', owner=self.user)
        self.course.students.add(self.user)
        self.module = Module.objects.create(course=self.course, title='Intro')

    def test_student_course_detail_shows_module(self):
        self.client.login(username='student4', password='pass')
        url = reverse('student_course_detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Organic Chemistry')
        self.assertContains(response, 'Intro')

    def test_student_course_detail_with_module_id(self):
        self.client.login(username='student4', password='pass')
        url = reverse('student_course_detail_module', args=[self.course.id, self.module.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Intro')
