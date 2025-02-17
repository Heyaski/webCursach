from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings
import uuid
from django.contrib.auth import login as auth_login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import User, UserProfile, Course, CourseEnrollment
from datetime import datetime
import logging
import socket
import ssl

logger = logging.getLogger(__name__)

def show(request):
    return render(request, "index.html")

def login(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('profiles')
            else:
                messages.error(request, 'Неверный логин или пароль')
        else:
            messages.error(request, 'Пожалуйста, заполните все поля')
    
    return render(request, "authorizationAccount.html")

def send_verification_email(user):
    try:
        subject = 'Подтверждение email для Академии MAST'
        verify_url = f"http://127.0.0.1:8000/verify/{user.verification_token}"
        
        context = {
            'user': user,
            'verify_url': verify_url,
            'site_name': 'Академия MAST'
        }
        
        text_message = render_to_string('email/verification.txt', context)
        html_message = render_to_string('email/verification.html', context)
        
        # Используем EmailMultiAlternatives для более надежной отправки
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            connection=None  # Django выберет соединение автоматически
        )
        
        email.attach_alternative(html_message, "text/html")
        
        # Добавляем больше информации для отладки
        logger.info(f"Attempting to send email to {user.email}")
        
        email.send(fail_silently=False)
        logger.info(f"Email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        return False

def verify_email(request, token):
    user = get_object_or_404(User, verification_token=token)
    user.email_verified = True
    user.verification_token = uuid.uuid4()  # Обновляем токен после использования
    user.save()
    messages.success(request, 'Email успешно подтвержден!')
    return redirect('profiles')

@csrf_protect
def resend_verification(request):
    if request.method == 'POST':
        if request.user.is_authenticated and not request.user.email_verified:
            try:
                success = send_verification_email(request.user)
                if success:
                    return JsonResponse({'status': 'success', 'message': 'Письмо отправлено'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Ошибка отправки письма'}, status=500)
            except Exception as e:
                logger.error(f"Error in resend_verification: {str(e)}", exc_info=True)
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def reg(request):
    if request.method == 'POST':
        username = request.POST['login']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        # Преобразуем значение чекбокса в булево
        agree = request.POST.get('data_processing_agreement', '') == 'on'

        if password != confirm_password:
            messages.error(request, 'Пароли не совпадают')
            return render(request, "registrationAccount.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким логином уже существует')
            return render(request, "registrationAccount.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с такой почтой уже существует')
            return render(request, "registrationAccount.html")

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                agree_to_processing=agree
            )
            send_verification_email(user)
            auth_login(request, user)
            messages.success(request, 'На вашу почту отправлено письмо для подтверждения email')
            return redirect('profiles')
        except Exception as e:
            messages.error(request, f'Ошибка при создании пользователя: {str(e)}')
            return render(request, "registrationAccount.html")

    return render(request, "registrationAccount.html")

@login_required
def prof(request):
    if request.method == 'POST':
        if 'profile_photo' in request.FILES:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.profile_photo = request.FILES['profile_photo']
            profile.save()
            return JsonResponse({'photo_url': profile.get_photo_url()})
        
        elif 'reset_photo' in request.POST:
            profile = request.user.profile
            if profile.profile_photo:
                profile.profile_photo.delete()
            profile.profile_photo = None
            profile.save()
            return JsonResponse({'photo_url': profile.DEFAULT_PHOTO_URL})

        if 'save_changes' in request.POST:
            # Обработка сохранения изменений профиля
            user = request.user
            user.russian_first_name = request.POST.get('first_name', '')
            user.russian_last_name = request.POST.get('last_name', '')
            user.save()
            messages.success(request, 'Изменения успешно сохранены')
            return redirect('profiles')
        
        elif 'change_password' in request.POST:
            # Обработка изменения пароля
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_new_password = request.POST.get('confirm_new_password')
            
            # Проверяем старый пароль
            if not request.user.check_password(old_password):
                messages.error(request, 'Неверный текущий пароль')
                return redirect('profiles')
            
            # Проверяем совпадение новых паролей
            if new_password != confirm_new_password:
                messages.error(request, 'Новые пароли не совпадают')
                return redirect('profiles')
            
            # Меняем пароль
            request.user.set_password(new_password)
            request.user.save()
            # Обновляем сессию, чтобы пользователь не выходил из системы
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Пароль успешно изменен')
            return redirect('profiles')
            
        elif 'save_info' in request.POST:
            # Обработка сохранения дополнительной информации
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            profile.about_me = request.POST.get('about_me', '')
            profile.city = request.POST.get('city', '')
            profile.phone = request.POST.get('phone', '')
            
            # Преобразование даты из строки в объект date
            birth_date = request.POST.get('birth_date')
            if birth_date:
                try:
                    profile.birth_date = datetime.strptime(birth_date, '%d.%m.%Y').date()
                except ValueError:
                    messages.error(request, 'Неверный формат даты')
                    return redirect('profiles')
            
            profile.save()
            messages.success(request, 'Информация успешно обновлена')
            return redirect('profiles')
            
        elif 'logout' in request.POST:
            # Обработка выхода из аккаунта
            logout(request)
            return redirect('home')
    
    # Создаем профиль при первом посещении страницы, если его нет
    UserProfile.objects.get_or_create(user=request.user)
    
    # Получаем статусы курсов для текущего пользователя
    enrollments = CourseEnrollment.objects.filter(user=request.user)
    enrollment_status = {}
    
    # Создаем словарь с простыми значениями для каждого курса
    for enrollment in enrollments:
        status = enrollment.status
        badge_class = {
            'pending': 'badge-warning',
            'approved': 'badge-success',
            'completed': 'badge-success',
        }.get(status, 'badge-secondary')
        
        status_text = {
            'pending': 'Ожидает подтверждения',
            'approved': 'Вы обучаетесь',
            'completed': 'Пройден',
        }.get(status, 'Не пройден')
        
        enrollment_status[enrollment.course.name] = {
            'status': status,
            'badge_class': badge_class,
            'text': status_text,
            'can_decline': status == 'pending'
        }
    
    context = {
        'enrollment_status': enrollment_status,
        'user': request.user,
    }
    return render(request, "profile.html", context)

@login_required
def cur(request):
    # Создаем профиль пользователя, если его нет
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Получаем все записи пользователя на курсы
    user_enrollments = CourseEnrollment.objects.filter(user=request.user).select_related('course')
    enrollment_status = {str(e.course.name): e.status for e in user_enrollments}
    
    context = {
        'enrollment_status': enrollment_status,
        'user_profile': user_profile,
        'user': request.user,  # Добавляем пользователя в контекст
        'courses': Course.objects.all()
    }
    return render(request, "cours.html", context)

@login_required
def enroll_course(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        address = request.POST.get('address')
        
        if not all([course_id, phone, city, address]):
            return JsonResponse({
                'status': 'error',
                'message': 'Пожалуйста, заполните все поля'
            })
        
        try:
            course = Course.objects.get(name=course_id)
            
            # Проверяем, есть ли уже запись
            existing_enrollment = CourseEnrollment.objects.filter(
                user=request.user, 
                course=course
            ).first()
            
            if existing_enrollment:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Вы уже записаны на этот курс'
                })
            
            # Создаем новую запись
            enrollment = CourseEnrollment.objects.create(
                user=request.user,
                course=course,
                phone=phone,
                city=city,
                address=address,
                status='pending'
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Заявка на обучение отправлена'
            })
            
        except Course.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Курс не найден'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Произошла ошибка при записи на курс'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Неверный метод запроса'
    })

def reset_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Генерируем новый токен
            user.verification_token = uuid.uuid4()
            user.save()
            
            # Формируем URL для сброса пароля
            reset_url = f"http://127.0.0.1:8000/set-password/{user.verification_token}"
            
            # Отправляем email
            subject = 'Восстановление пароля'
            html_message = render_to_string('email/reset_password.html', {
                'reset_url': reset_url
            })
            text_message = strip_tags(html_message)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            messages.success(request, 'Инструкции по восстановлению пароля отправлены на вашу почту')
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')
    
    return render(request, 'reset_password.html')

def set_new_password(request, token):
    try:
        user = User.objects.get(verification_token=token)
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password == confirm_password:
                user.set_password(new_password)
                user.verification_token = uuid.uuid4()  # Обновляем токен
                user.save()
                messages.success(request, 'Пароль успешно изменен')
                return redirect('login')
            else:
                messages.error(request, 'Пароли не совпадают')
        
        return render(request, 'set_new_password.html')
        
    except User.DoesNotExist:
        messages.error(request, 'Недействительная ссылка для восстановления пароля')
        return redirect('login')

def send_course_approval_email(enrollment):
    try:
        subject = f'Заявка на курс "{enrollment.course.get_name_display()}" одобрена'
        
        context = {
            'enrollment': enrollment,
        }
        
        html_content = render_to_string('email/course_approved.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[enrollment.user.email]
        )
        
        email.attach_alternative(html_content, "text/html")
        
        # Прикрепляем файл курса, если он есть
        if enrollment.course.course_file:
            email.attach_file(enrollment.course.course_file.path)
        
        email.send()
        return True
    except Exception as e:
        logger.error(f"Error sending course approval email: {str(e)}", exc_info=True)
        return False

# Обновляем админский интерфейс для обработки статуса записи
@login_required
def update_enrollment_status(request, enrollment_id):
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Недостаточно прав'})
        
    try:
        enrollment = CourseEnrollment.objects.get(id=enrollment_id)
        new_status = request.POST.get('status')
        
        if new_status == 'approved':
            enrollment.status = 'approved'
            enrollment.save()
            
            # Отправляем письмо с файлом курса
            if send_course_approval_email(enrollment):
                return JsonResponse({
                    'status': 'success',
                    'message': 'Статус обновлен и письмо отправлено'
                })
            else:
                return JsonResponse({
                    'status': 'warning',
                    'message': 'Статус обновлен, но возникла проблема с отправкой письма'
                })
                
        return JsonResponse({'status': 'error', 'message': 'Неверный статус'})
        
    except CourseEnrollment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Запись не найдена'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def decline_course(request, enrollment_id):
    try:
        # Получаем название курса на основе ID
        course_name = f'course-{enrollment_id}'
        
        # Ищем запись о курсе для текущего пользователя
        enrollment = CourseEnrollment.objects.filter(
            course__name=course_name,
            user=request.user,
            status='pending'
        ).first()
        
        if enrollment:
            # Удаляем запись
            enrollment.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Вы успешно отказались от курса'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Запись на курс не найдена'
            }, status=404)
            
    except Exception as e:
        print(f"Error in decline_course: {str(e)}")  # Для отладки
        return JsonResponse({
            'status': 'error',
            'message': 'Произошла ошибка при отказе от курса'
        }, status=500)