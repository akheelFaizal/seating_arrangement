"""
URL configuration for seating_arrangement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [

    #student

    path('',views.StudentLogin, name="studentlogin"),
    path('student/overview',views.StudentOverView),
    path('student/seatview',views.StudentSeatview),
    path('student/resultview',views.StudentResultView),
    path('student/examdetail',views.StudentExamDetail),
    path('student/signupaction',views.StudentSignupAction),

    #admin
    path('admin', views.index),
    path('student-management/',views.StudentManagement),
    path('seating-arrangement/',views.SeatingArrangement),
    path('exam/',views.ExamSchedule)

]
