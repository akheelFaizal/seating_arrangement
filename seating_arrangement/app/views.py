from django.shortcuts import render, redirect


def index(request):
    return render(request, 'p1.html')


def StudentLogin(request):
    return render(request, 'studentLogin.html')