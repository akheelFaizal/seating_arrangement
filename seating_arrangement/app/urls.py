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
    path('student/signupaction',views.StudentSignupAction),

    #admin
    path('adminhome', views.index),
    path('student-management/',views.StudentManagement),
    path('seating-arrangement/',views.SeatingArrangement),
    path('exam/',views.ExamSchedule),


    #invigilator

    path('invigilator/teacheroverview',views.teacheroverview),

    # admin
    path('', views.index, name='index'),
    path('student-management/', views.StudentManagement, name='student_management'),
    path('seating-arrangement/', views.SeatingArrangement, name='seating_arrangement'),
    path('exam/', views.ExamSchedule, name='exam_schedule'),
    
    # admin functionalities
    path('upload_students/', views.upload_students, name='upload_students'),
    path('add_room/', views.add_room, name='add_room'),
    path('assign_seats/<int:exam_id>/', views.assign_seats, name='assign_seats'),
    path("add-exam/", views.add_exam, name="add_exam"),
    path('edit-exam/<int:exam_id>/', views.edit_exam, name='edit_exam'),
    path('delete-exam/<int:exam_id>/', views.delete_exam, name='delete_exam'),
    # path('students/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),

]


