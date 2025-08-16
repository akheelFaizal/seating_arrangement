from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password


def index(request):
      return render(request, 'admin/Admin.html')

#student


def StudentLogin(request):
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        password_raw = request.POST.get('password')

        try:
            student = Student.objects.get(roll_number=roll_number)
        except Student.DoesNotExist:
            messages.error(request, "Invalid roll number or password.")
            return redirect(StudentLogin)

        if check_password(password_raw, student.password):
            request.session['student_id'] = student.id  # simple session login
            messages.success(request, "Login successful!")
            return redirect(StudentOverView)  # or wherever is appropriate
        else:
            messages.error(request, "Invalid roll number or password.")
            return redirect(StudentLogin)

    return render(request, 'student/studentLogin.html')


def StudentSignupAction(request):

    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        name = request.POST.get('name')
        password_raw = request.POST.get('password')
        department_id = request.POST.get('department')
        course_id = request.POST.get('course')

        # Check duplicate roll number
        if Student.objects.filter(roll_number=roll_number).exists():
            messages.error(request, "Roll number already exists.")
            return redirect(StudentSignupAction)

        # Hash the password (important for security)
        password = make_password(password_raw)

        try:
            department = Department.objects.get(id=department_id)
            course = Course.objects.get(id=course_id)
        except (Department.DoesNotExist, Course.DoesNotExist):
            messages.error(request, "Invalid department or course selected.")
            return redirect(StudentSignupAction)

        student = Student(
            roll_number=roll_number,
            name=name,
            password=password,
            department=department,
            course=course
        )
        student.save()
        messages.success(request, "Signup successful! Please login.")
        return redirect(StudentLogin)

    # For GET, show signup form with department and course options
    departments = Department.objects.all()
    courses = Course.objects.all()
    return render(request, 'student/StudentSignup.html', {'departments': departments, 'courses': courses})


def StudentOverView(request):

    student_id = request.session.get('student_id')
    student = Student.objects.get(id=student_id)

    # Fetch exam seats for this student
    # exam_seats = ExamSeat.objects.filter(student=student)

    # Fetch hall ticket URL (assuming student.hall_ticket_pdf exists)
    # hall_ticket_url = student.hall_ticket_pdf.url if student.hall_ticket_pdf else None

    # Fetch Announcements
    # announcements = Announcement.objects.order_by('-date')[:3]  # Latest 3

    context = {
        'student': student,
        # 'exam_seats': exam_seats,
        # 'hall_ticket_url': hall_ticket_url,
        # 'announcements': announcements,
    }

    return render(request, 'student/studentOverView.html',context)

def StudentSeatview(request):
    return render(request, 'student/studentSeatview.html')

def StudentResultView(request):
    return render(request, 'student/studentResultView.html')

def StudentExamDetail(request):
    return render(request,'student/StudentExamDetail.html')\
    
#admin

def StudentManagement(request):
    departments = Department.objects.all()
    print(departments)
    return render(request, 'admin/StudentManagement.html', {'departments':departments})
  
def SeatingArrangement(request):
    return render(request, 'admin/SeatingArrangement.html')

  
def ExamSchedule(request):
    return render(request, 'admin/ExamSchedule.html')

  
  

