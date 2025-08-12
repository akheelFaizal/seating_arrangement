from django.shortcuts import render, redirect


def index(request):
      return render(request, 'admin/Admin.html')


def StudentLogin(request):
    return render(request, 'student/studentLogin.html')

def StudentOverView(request):
    return render(request, 'student/studentOverView.html')

  
def StudentManagement(request):
    return render(request, 'admin/StudentManagement.html')
  
def SeatingArrangement(request):
    return render(request, 'admin/SeatingArrangement.html')

  
def ExamSchedule(request):
    return render(request, 'admin/ExamSchedule.html')

  
  

