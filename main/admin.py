from django.contrib import admin
from django.contrib import messages
from .models import User, UserProfile, Course, CourseEnrollment
from .views import send_course_approval_email

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'russian_first_name', 'russian_last_name', 'email_verified']
    search_fields = ['username', 'email', 'russian_first_name', 'russian_last_name']
    list_filter = ['email_verified']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'phone', 'birth_date']
    search_fields = ['user__username', 'city', 'phone']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'instructor']
    search_fields = ['name', 'instructor']

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user_info', 'course', 'status', 'phone', 'city', 'address', 'created_at']
    list_filter = ['status', 'course', 'city']
    search_fields = ['user__username', 'user__email', 'user__russian_first_name', 'user__russian_last_name', 'phone', 'city']
    list_editable = ['status']
    
    def user_info(self, obj):
        return f"{obj.user.russian_last_name} {obj.user.russian_first_name} ({obj.user.email})"
    user_info.short_description = 'Пользователь'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if 'status' in form.changed_data and obj.status == 'approved':
            if send_course_approval_email(obj):
                messages.success(request, f'Письмо успешно отправлено пользователю {obj.user.email}')
            else:
                messages.error(request, f'Ошибка при отправке письма пользователю {obj.user.email}')
