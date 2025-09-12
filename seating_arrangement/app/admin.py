# from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import *


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # optional: show extra fields if you added any
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("phone_number","roll_number")}),  # add custom field
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("phone_number","roll_number")}),
    )

admin.site.register(CustomUser, CustomUserAdmin)


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