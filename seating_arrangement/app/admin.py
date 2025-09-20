# from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import *


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ("roll_number",)
    list_display = ("roll_number", "name", "email", "role", "course", "department", "year", "is_staff")
    list_filter = ("role", "department", "course", "is_staff")
    search_fields = ("roll_number", "name", "email")

    fieldsets = (
        (None, {"fields": ("roll_number", "password")}),
        ("Personal info", {"fields": ("name", "email")}),
        ("Academic", {"fields": ("course", "department", "year")}),
        ("Role", {"fields": ("role",)}),  # 👈 added role here
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("roll_number", "name", "email", "course", "department", "year", "role", "password1", "password2"),
        }),
    )



#student info

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'department']
    list_filter = ['department']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'roll_number', 'name', 'course', 'department']
    search_fields = ['name', 'roll_number']
    list_filter = ['department', 'course']


#invigilator info

@admin.register(Invigilator)
class InvigilatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'phone']
    search_fields = ['name', 'email']
    list_filter = ['name']




#exam info


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['subject_code', 'subject_name', 'department']
    list_filter = ['department']
    search_fields = ['subject_name', 'subject_code']


#room info

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'room_number', 'capacity', 'supervisor']
    search_fields = ['room_number']
    list_filter = ['supervisor']

#seating info


@admin.register(Seating)
class SeatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'exam', 'room', 'seat_number']
    list_filter = ['exam', 'room']
    search_fields = ['student__name', 'student__roll_number', 'exam__subject_name']

admin.site.register(ExamSession)