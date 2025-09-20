from django.db import models
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser

# Create your models here.

from django.db import models
from django.contrib.auth.hashers import make_password

#student tables

class Department(models.Model):
    name = models.CharField(max_length=100)

    def _str_(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def _str_(self):
        return self.name



class CustomUser(AbstractUser):
    # username will be roll_number for students or employee_id for invigilators
    name = models.CharField(max_length=100, blank=True, null=True)
    course = models.ForeignKey("Course", on_delete=models.CASCADE, blank=True, null=True)
    department = models.ForeignKey("Department", on_delete=models.CASCADE, blank=True, null=True)
    year = models.PositiveIntegerField(
        choices=[(1, "1st Year"), (2, "2nd Year"), (3, "3rd Year"), (4, "4th Year")],
        blank=True, null=True
    )
    
    # New fields for invigilator support
    ROLE_CHOICES = (
        ("student", "Student"),
        ("invigilator", "Invigilator"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    # For invigilators
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    invigilator_department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name or self.username} ({self.role})"




    
class Student(models.Model):
    roll_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    year = models.PositiveIntegerField(
        choices=[(1, "1st Year"), (2, "2nd Year"), (3, "3rd Year"), (4, "4th Year")],
        default=1
    )

    def _str_(self):
        return f"{self.name} ({self.roll_number})"
    

#invigilator

class Invigilator(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(unique=True)

    def _str_(self):
        return self.name



#exam details
    
class ExamSession(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def _str_(self):
        return f"{self.date} {self.start_time}-{self.end_time}"


class Exam(models.Model):
    subject_code = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name="exams", default=1)

    def _str_(self):
        return self.subject_name


#room info

class Room(models.Model):
    room_number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField()
    supervisor = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    bench_capacity = models.IntegerField(default=3)
    rows = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1)])
    columns = models.PositiveIntegerField(default=2, validators=[MinValueValidator(1)])
    
    def _str_(self):
        return self.room_number


#seating info
class Seating(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField()

class NewsUpdate(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('teacher', 'Teacher')])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def _str_(self):
        return self.title