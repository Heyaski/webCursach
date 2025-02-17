"""
URL configuration for mast project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.show, name='home'),
    path('login', views.login, name='login'),
    path('registration', views.reg, name='registr'),
    path('profile/', views.prof, name='profiles'),
    path('courses', views.cur, name='courses'),
    path('verify/<uuid:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('reset-password/', views.reset_password_request, name='reset_password_request'),
    path('set-password/<uuid:token>/', views.set_new_password, name='set_new_password'),
    path('enroll-course/', views.enroll_course, name='enroll_course'),
    path('decline-course/<int:enrollment_id>/', views.decline_course, name='decline_course'),
]
