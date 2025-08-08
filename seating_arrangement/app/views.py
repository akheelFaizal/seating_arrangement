from django.shortcuts import render, redirect


def index(request):
      return render(request, 'admin/Admin.html')


def StudentLogin(request):
    return render(request, 'student/studentLogin.html')

  
def StudentManagement(request):
    return render(request, 'admin/StudentManagement.html')

  

