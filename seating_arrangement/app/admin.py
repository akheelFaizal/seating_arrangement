# from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import *


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Show important fields in admin list
    list_display = (
        "username", "first_name", "role", "course", "department", "year",
        "employee_id", "invigilator_department", "is_staff"
    )
    search_fields = ("username", "name", "email", "employee_id")

    # Add custom fields to the default fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ("Academic info", {"fields": ("course", "department", "year")}),
        ("Invigilator info", {"fields": ("role", "employee_id", "invigilator_department")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Academic info", {"fields": ("course", "department", "year")}),
        ("Invigilator info", {"fields": ("role", "employee_id", "invigilator_department")}),
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
    search_fields = ['student_name', 'studentroll_number', 'exam_subject_name']

admin.site.register(ExamSession)