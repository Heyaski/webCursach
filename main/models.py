from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    agree_to_processing = models.BooleanField(default=False)
    russian_first_name = models.CharField(max_length=30, blank=True)
    russian_last_name = models.CharField(max_length=30, blank=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    about_me = models.TextField(max_length=300, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    
    DEFAULT_PHOTO_URL = 'https://bootdey.com/img/Content/avatar/avatar1.png'

    def get_photo_url(self):
        if self.profile_photo:
            return self.profile_photo.url
        return self.DEFAULT_PHOTO_URL

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"

class Course(models.Model):
    COURSE_CHOICES = [
        ('course-1', 'Мастерство с нуля'),
        ('course-2', 'От контуров к шедеврам'),
        ('course-3', 'Искусство на коже'),
    ]
    
    name = models.CharField(max_length=100, choices=COURSE_CHOICES)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    course_file = models.FileField(upload_to='course_files/', null=True, blank=True)
    
    def __str__(self):
        return self.get_name_display()

class CourseEnrollment(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Не пройден'),
        ('pending', 'Ожидает подтверждения'),
        ('approved', 'Подтверждено'),
        ('completed', 'Пройден'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    created_at = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ['user', 'course']  # Пользователь может записаться на курс только один раз
    
    def __str__(self):
        return f"{self.user.username} - {self.course.get_name_display()} ({self.get_status_display()})"
