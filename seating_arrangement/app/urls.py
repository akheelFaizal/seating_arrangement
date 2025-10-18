from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

    # -----------------------
    # Invigilator Management
    # -----------------------
    path("invigilators/", views.invigilator_management, name="invigilator_management"),
    path("add/invigilators/", views.add_invigilator, name="add_invigilator"),
    path("invigilators/assign/<int:invigilator_id>/", views.assign_invigilator_room, name="assign_invigilator_room"),
    path('invigilator/delete/<int:id>/', views.delete_invigilator, name='delete_invigilator'),

    # Invigilator profile
    path("invigilator/invigilatorOverview", views.invigilator_dashboard, name="invigilatordashboard"),
    path("invigilator/seatarrangement", views.invigilatorSeatarrangement, name="invigilatorseatarrangement"),
    path("invigilator/profile", views.invigilatorProfile, name="invigilatorprofile"),
    path('invigilator/profile/edit/', views.edit_invigilator_profile, name='edit_invigilator_profile'),

    # -----------------------
    # Student Management
    # -----------------------
    path('student/<int:id>/reinstate/', views.reinstate_student, name='reinstate_student'),
    path('student/user/delete/<int:id>/', views.delete_student_user, name='delete_student_user'),
    path("student/login/", views.login_view, name="login"),
    path('logout/', views.student_logout, name='student_logout'),
    path('student/overview/', views.StudentOverView, name='student_overview'),
    path('student/seatview/', views.StudentSeatview, name='student_seatview'),
    path('student/examdetail/', views.StudentExamDetail, name='student_examdetail'),
    path("", views.signup, name="signup"),
    path('add/student/', views.student_add, name='student_add'),
    path('edit/student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete/student/<int:student_id>/', views.delete_student, name='delete_student'),
    path("students/edit/", views.edit_student, name="edit_student"),
    path("students/bulk-delete/", views.bulk_delete_students, name="bulk_delete_students"),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),

    # student
    
    # path('student/login/', views.StudentLogin, name='student_login'),
    path("student/login/", views.login_view, name="login"),
    path('logout/', views.student_logout, name='student_logout'),
    path('student/overview/', views.StudentOverView, name='student_overview'),
    path('student/seatview/', views.StudentSeatview, name='student_seatview'),
    path('student/examdetail/', views.StudentExamDetail, name='student_examdetail'),
    # path('student/signupaction',views.StudentSignupAction),
    path("",views.signup, name="signup"),

    # -----------------------
    # Admin Management
    # -----------------------
    path('student-management/', views.StudentManagement, name='student_management'),
    path('seating-arrangement/', views.SeatingArrangement, name='seating_arrangement'),
    path('exam/', views.ExamSchedule, name='exam_schedule'),
    path('room-management/', views.room_management, name='room_management'),
    path('news-management/', views.NewsManagement, name='news_updates'),
    path('analytics/', views.analytics, name='analytics'),
    path('debar-management/', views.debarmanagement, name="debar-management"),
    # Upload and add
    path('upload_students/', views.upload_students, name='upload_students'),
    path('add_room/', views.add_room, name='add_room'),
    path('delete-news/<int:news_id>/', views.delete_news, name='delete_news'),
    path("add-exam/", views.add_exam, name="add_exam"),

    # Edit and Delete
    path('edit-exam/<int:exam_id>/', views.edit_exam, name='edit_exam'),
    path('delete-exam/<int:exam_id>/<int:department_id>/', views.delete_exam, name='delete_exam'),
    path('room/<int:room_id>/map/', views.seating_map_detail, name='seating_map_detail'),
    path('seating/assign_by_date/', views.assign_seats_by_date, name='assign_seats_by_date'),
    path('seating/remove_all/', views.remove_all_assignments, name='remove_all_assignments'),
    path("rooms/", views.room_management, name="room_management"),
    path("rooms/edit/<int:pk>/", views.room_edit, name="room_edit"),
    path("rooms/delete/<int:pk>/", views.room_delete, name="room_delete"),
    path("news/approve/<int:pk>/", views.news_approve, name="news_approve"),
    path("news/reject/<int:pk>/", views.news_reject, name="news_reject"),
    path("add/session/", views.add_session, name="add_session"),


        
        

        # admin
        
        path('index', views.index, name='index'),
        path('student-management/', views.StudentManagement, name='student_management'),
        path('seating-arrangement/', views.SeatingArrangement, name='seating_arrangement'),
        path('exam/', views.ExamSchedule, name='exam_schedule'),
        path('room-management/', views.room_management, name='room_management'),
        path('news-management/', views.NewsManagement, name='news_updates'),
        path('analytics/', views.analytics, name='analytics'),
        path('debar-management/',views.debarmanagement,name="debar-management"),

        
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
        path("add/session/", views.add_session, name="add_session"),

        #invigilator 
        path("invigilator/invigilatorOverview",views.invigilator_dashboard,name="invigilatordashboard"),
        path("invigilator/seatarrangement",views.invigilatorSeatarrangement,name="invigilatorseatarrangement"),
        path("invigilator/profile",views.invigilatorProfile,name="invigilatorprofile"),
        # path("invigilator/signup",views.invigilator_signup,name="invigilatorsignup")
        path('invigilator/profile/edit/', views.edit_invigilator_profile, name='edit_invigilator_profile'),
        path('invigilator/students/', views.invigilatorAssignedStudents, name="invigilator_assigned_students"),



        # login and logout
       

    # -----------------------
    # Admin Home
    # -----------------------
    path('index', views.index, name='index'),

]
