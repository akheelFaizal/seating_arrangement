from django.shortcuts import render, redirect
from . models import *

def index(request):
      return render(request, 'admin/Admin.html')

#student

def StudentLogin(request):
    return render(request, 'student/studentLogin.html')

def StudentOverView(request):
    return render(request, 'student/studentOverView.html')

def StudentSeatview(request):
    return render(request, 'student/studentSeatview.html')

def StudentResultView(request):
    return render(request, 'student/studentResultView.html')

def StudentExamDetail(request):
    return render(request,'student/StudentExamDetail.html')
  

#admin

def StudentManagement(request):
    departments = Department.objects.all()
    print(departments)
    return render(request, 'admin/StudentManagement.html', {'departments':departments})
  
def SeatingArrangement(request):
    return render(request, 'admin/SeatingArrangement.html')

  
def ExamSchedule(request):
    return render(request, 'admin/ExamSchedule.html')

  
  

