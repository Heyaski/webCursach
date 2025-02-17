from django.contrib import admin
from django.contrib import messages
from .models import User, UserProfile, Course, CourseEnrollment
from .views import send_course_approval_email

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'instructor']
    search_fields = ['name', 'instructor']

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'created_at']
    list_filter = ['status', 'course']
    search_fields = ['user__username', 'user__email']
    list_editable = ['status']
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Если статус меняется на "approved"
        if 'status' in form.changed_data and obj.status == 'approved':
            if send_course_approval_email(obj):
                messages.success(request, f'Письмо успешно отправлено пользователю {obj.user.email}')
            else:
                messages.error(request, f'Ошибка при отправке письма пользователю {obj.user.email}')
