from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

    # student
    path('student/login/', views.StudentLogin, name='student_login'),
    path('student/overview/', views.StudentOverView, name='student_overview'),
    path('student/seatview/', views.StudentSeatview, name='student_seatview'),
    path('student/resultview/', views.StudentResultView, name='student_resultview'),
    path('student/examdetail/', views.StudentExamDetail, name='student_examdetail'),

    # admin
    path('', views.index, name='index'),
    path('student-management/', views.StudentManagement, name='student_management'),
    path('seating-arrangement/', views.SeatingArrangement, name='seating_arrangement'),
    path('exam/', views.ExamSchedule, name='exam_schedule'),
    
    # functionalities
    path('upload_students/', views.upload_students, name='upload_students'),
    path('add_room/', views.add_room, name='add_room'),
    path('assign_seats/<int:exam_id>/', views.assign_seats, name='assign_seats'),
]
