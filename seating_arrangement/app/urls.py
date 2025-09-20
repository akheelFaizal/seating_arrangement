from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

        # student
        # path('student/login/', views.StudentLogin, name='student_login'),
        path("student/login/", views.login_view, name="login"),
        path("student/logout/", views.logout_view, name="logout"),
        path('student/overview/', views.StudentOverView, name='student_overview'),
        path('student/seatview/', views.StudentSeatview, name='student_seatview'),
        path('student/resultview/', views.StudentResultView, name='student_resultview'),
        path('student/examdetail/', views.StudentExamDetail, name='student_examdetail'),
        # path('student/signupaction',views.StudentSignupAction),
        path("student/signup/",views.signup, name="signup"),

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
        path('room-management/', views.room_management, name='room_management'),
        path('news-management/', views.NewsManagement, name='news_updates'),
        path('analytics/', views.analytics, name='analytics'),

        
        # admin functionalities
        path('upload_students/', views.upload_students, name='upload_students'),
        path('add_room/', views.add_room, name='add_room'),
        path("add-exam/", views.add_exam, name="add_exam"),
        path('edit-exam/<int:exam_id>/', views.edit_exam, name='edit_exam'),
        path('delete-exam/<int:exam_id>/', views.delete_exam, name='delete_exam'),
        path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),

        path('room/<int:room_id>/map/', views.seating_map_detail, name='seating_map_detail'),
        path('seating/assign_by_date/', views.assign_seats_by_date, name='assign_seats_by_date'),
        path('seating/remove_all/', views.remove_all_assignments, name='remove_all_assignments'),




        path("rooms/", views.room_management, name="room_management"),
        path("rooms/edit/<int:pk>/", views.room_edit, name="room_edit"),
        path("rooms/delete/<int:pk>/", views.room_delete, name="room_delete"),
        path("news/approve/<int:pk>/", views.news_approve, name="news_approve"),
        path("news/reject/<int:pk>/", views.news_reject, name="news_reject"),

        #invigilator 
        path("invigilator/invigilatorOverview",views.invigilator_dashboard,name="invigilatordashboard"),
        path("invigilator/seatarrangement",views.invigilatorSeatarrangement),
        path("invigilator/profile",views.invigilatorProfile,name="invigilatorprofile")


        # login and logout
       
]


