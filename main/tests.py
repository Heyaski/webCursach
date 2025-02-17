from django.test import TestCase, Client
from django.urls import reverse
from .models import User, UserProfile, Course, CourseEnrollment
from django.core import mail

class UserModelTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            russian_first_name='Иван',
            russian_last_name='Иванов'
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.russian_first_name, 'Иван')
        self.assertEqual(self.user.russian_last_name, 'Иванов')
        self.assertFalse(self.user.email_verified)

class CourseModelTest(TestCase):
    def setUp(self):
        # Создаем тестовый курс
        self.course = Course.objects.create(
            name='course-1',
            description='Test course description',
            instructor='Test Instructor'
        )

    def test_course_creation(self):
        """Тест создания курса"""
        self.assertEqual(self.course.name, 'course-1')
        self.assertEqual(self.course.get_name_display(), 'Мастерство с нуля')
        self.assertEqual(self.course.instructor, 'Test Instructor')

class ViewsTest(TestCase):
    def setUp(self):
        # Создаем тестового клиента
        self.client = Client()
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Создаем тестовый курс
        self.course = Course.objects.create(
            name='course-1',
            description='Test course description',
            instructor='Test Instructor'
        )

    def test_login_page(self):
        """Тест страницы входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authorizationAccount.html')

    def test_login_functionality(self):
        """Тест функционала входа"""
        response = self.client.post(reverse('login'), {
            'login': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа
        self.assertRedirects(response, reverse('profiles'))

    def test_enroll_course(self):
        """Тест записи на курс"""
        # Входим как пользователь
        self.client.login(username='testuser', password='testpass123')
        
        # Отправляем запрос на запись
        response = self.client.post(reverse('enroll_course'), {
            'course_id': 'course-1',
            'phone': '+7 (999) 999-99-99',
            'city': 'Москва',
            'address': 'Test Address'
        })
        
        # Проверяем ответ
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        # Проверяем создание записи
        enrollment = CourseEnrollment.objects.filter(
            user=self.user,
            course=self.course
        ).first()
        
        # Заменяем assertIsNotEmpty на правильную проверку
        self.assertIsNotNone(enrollment)  # Проверяем что запись существует
        self.assertEqual(enrollment.status, 'pending')

    def test_verification_email(self):
        """Тест отправки verification email"""
        self.client.post(reverse('registr'), {
            'login': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'confirm_password': 'newpass123',
            'data_processing_agreement': 'on'
        })
        
        # Проверяем, что email был отправлен
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Подтверждение email для Академии MAST')

class CourseEnrollmentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            name='course-1',
            description='Test course description',
            instructor='Test Instructor'
        )

    def test_enrollment_creation(self):
        """Тест создания записи на курс"""
        enrollment = CourseEnrollment.objects.create(
            user=self.user,
            course=self.course,
            status='pending',
            phone='+7 (999) 999-99-99',
            city='Москва',
            address='Test Address'
        )
        
        self.assertEqual(enrollment.user, self.user)
        self.assertEqual(enrollment.course, self.course)
        self.assertEqual(enrollment.status, 'pending')

    def test_unique_enrollment(self):
        """Тест уникальности записи на курс"""
        CourseEnrollment.objects.create(
            user=self.user,
            course=self.course,
            status='pending',
            phone='+7 (999) 999-99-99',
            city='Москва',
            address='Test Address'
        )
        
        # Проверяем, что нельзя создать вторую запись
        with self.assertRaises(Exception):
            CourseEnrollment.objects.create(
                user=self.user,
                course=self.course,
                status='pending',
                phone='+7 (999) 999-99-99',
                city='Москва',
                address='Test Address'
            )
