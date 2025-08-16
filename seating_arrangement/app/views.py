from django.shortcuts import render, redirect
from . models import *
from django.contrib import messages
import csv
import random
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
    rooms = Room.objects.all()
    print(rooms)
    return render(request, 'admin/SeatingArrangement.html', {'rooms': rooms})

  
def ExamSchedule(request):
    return render(request, 'admin/ExamSchedule.html')


# functionalities


def upload_students(request):
    if request.method == "POST" and request.FILES.getlist("files"):
        files = request.FILES.getlist("files")
        
        for csv_file in files:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                dept, _ = Department.objects.get_or_create(name=row['Department'])
                course, _ = Course.objects.get_or_create(name=row['Course'], department=dept)
                Student.objects.update_or_create(
                    roll_number=row['Roll Number'],
                    defaults={
                        'name': row['Name'],
                        'department': dept,
                        'course': course
                    }
                )
        messages.success(request, "All student files uploaded successfully.")
    else:
        messages.error(request, "No files were selected for upload.")
    
    return redirect("seating_arrangement")


def add_room(request):
    if request.method == "POST":
        room_number = request.POST.get("room_number")
        capacity = request.POST.get("capacity")
        supervisor_id = request.POST.get("supervisor")
        supervisor = None
        if supervisor_id:
            from .models import Invigilator
            supervisor = Invigilator.objects.get(id=supervisor_id)
        Room.objects.create(room_number=room_number, capacity=int(capacity), supervisor=supervisor)
        messages.success(request, f"Room {room_number} added successfully.")
    return redirect("seating_arrangement")



def assign_seats(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    
    # Clear previous allocations
    Seating.objects.filter(exam=exam).delete()

    # Fetch all students for this exam
    students = list(Student.objects.all())
    rooms = list(Room.objects.all())
    
    # Shuffle students globally (all departments)
    random.shuffle(students)
    
    # Initialize room seat trackers
    room_indices = {room.id: 0 for room in rooms}
    
    # Keep track of last course in each room to avoid consecutive same-course seating
    last_course_in_room = {room.id: None for room in rooms}
    
    for student in students:
        # List of rooms that are not full
        available_rooms = [room for room in rooms if room_indices[room.id] < room.capacity]
        if not available_rooms:
            break  # No seats left
        
        # Filter rooms to avoid same-course neighbors if possible
        filtered_rooms = [room for room in available_rooms 
                          if last_course_in_room[room.id] != student.course]
        if filtered_rooms:
            chosen_room = random.choice(filtered_rooms)
        else:
            # If all rooms have same-course last student, pick randomly
            chosen_room = random.choice(available_rooms)
        
        # Assign seat
        seat_number = room_indices[chosen_room.id] + 1
        Seating.objects.create(
            student=student,
            exam=exam,
            room=chosen_room,
            seat_number=seat_number
        )
        
        # Update trackers
        room_indices[chosen_room.id] += 1
        last_course_in_room[chosen_room.id] = student.course

    messages.success(request, "Seats assigned successfully with anti-cheat logic.")
    return redirect("seating_arrangement")

  
  

