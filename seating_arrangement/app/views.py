from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from . models import *
from django.contrib import messages
import csv
import random
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from datetime import timedelta
import csv
from django.http import HttpResponse



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

    # Get filters from GET request
    dept_filter = request.GET.get("department")
    year_filter = request.GET.get("year")
    search_query = request.GET.get("search")
    export = request.GET.get("export", None)


    # Start with all students
    students = Student.objects.all()

    # Apply filters
    if dept_filter and dept_filter != "all":
        students = students.filter(department__id=dept_filter)

    if year_filter and year_filter != "all":
        students = students.filter(year=year_filter)

    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(roll_number__icontains=search_query)
        )

    if export == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="students.csv"'

        writer = csv.writer(response)
        writer.writerow(["Roll No", "Name", "Department", "Year", "Seat Info"])

        for student in students:
            seat_info = ", ".join(
                [f"{s.room.room_number} (Seat {s.seat_number})" for s in student.seating_set.all()]
            ) or "Not Assigned"
            writer.writerow([
                student.roll_number,
                student.name,
                student.department.name,
                student.year,
                seat_info,
            ])
        return response

    # Prefetch related seating to avoid N+1 queries
    students = students.prefetch_related("seating_set__room")

    return render(request, "admin/StudentManagement.html", {
        "departments": departments,
        "students": students,
        "selected_dept": dept_filter,
        "selected_year": year_filter,
        "search_query": search_query,
    })

  
def SeatingArrangement(request):
    rooms = Room.objects.all()
    exams = Exam.objects.all().first()
    print(rooms)
    return render(request, 'admin/SeatingArrangement.html', {'rooms': rooms, 'exam':exams})

  
def ExamSchedule(request):
    exams = Exam.objects.all().order_by("date", "time")
    departments = Department.objects.all() 
    return render(request, 'admin/ExamSchedule.html', {'exams':exams, 'departments':departments})


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
        messages.success(request, "All student files uploaded successfully!")  
    else:
        messages.error(request, "No files were selected for upload!")          
    
    return redirect("seating_arrangement")


def add_room(request):
    if request.method == "POST":
        room_number = request.POST.get("room_number")
        capacity = request.POST.get("capacity")
        supervisor_id = request.POST.get("supervisor")
        supervisor = None
        if supervisor_id:
            supervisor = Invigilator.objects.get(id=supervisor_id)
        Room.objects.create(room_number=room_number, capacity=int(capacity), supervisor=supervisor)
        messages.success(request, f"Room {room_number} added successfully!")   
    
    return redirect("seating_arrangement")


def assign_seats(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    Seating.objects.filter(exam=exam).delete()

    students = list(Student.objects.all())
    rooms = list(Room.objects.all())

    # Group students by class (course+year+section)
    from collections import defaultdict
    class_groups = defaultdict(list)
    for student in students:
        class_groups[(student.course, student.year, student.section)].append(student)

    # Shuffle inside each class group
    for group in class_groups.values():
        random.shuffle(group)

    # Flatten in round-robin order
    distributed_students = []
    while any(class_groups.values()):
        for key in list(class_groups.keys()):
            if class_groups[key]:
                distributed_students.append(class_groups[key].pop())

    # Now assign seats room by room
    room_indices = {room.id: 0 for room in rooms}
    student_index = 0

    for student in distributed_students:
        # Find next available room
        chosen_room = None
        for room in rooms:
            if room_indices[room.id] < room.capacity:
                chosen_room = room
                break
        if not chosen_room:
            break  # no seats left

        seat_number = room_indices[chosen_room.id] + 1
        Seating.objects.create(
            student=student,
            exam=exam,
            room=chosen_room,
            seat_number=seat_number
        )
        room_indices[chosen_room.id] += 1
        student_index += 1

    messages.success(request, "Seats assigned successfully with strict anti-cheat logic.")
    return redirect("seating_arrangement")

  

def add_exam(request):
    if request.method == "POST":
        subject_code = request.POST.get("subject_code")
        subject_name = request.POST.get("subject_name")
        department_id = request.POST.get("department")
        date = request.POST.get("date")
        time = request.POST.get("time")
        duration_str = request.POST.get("duration")  # e.g. "02:00:00"

        # Convert duration string ("HH:MM:SS") to timedelta
        try:
            hours, minutes, seconds = map(int, duration_str.split(":"))
            duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except ValueError:
            messages.error(request, "Invalid duration format. Please use HH:MM:SS.")
            return redirect("exam_schedule")

        department = Department.objects.get(id=department_id)

        Exam.objects.create(
            subject_code=subject_code,
            subject_name=subject_name,
            department=department,
            date=date,
            time=time,
            duration=duration
        )

        messages.success(request, f"Exam '{subject_name}' added successfully!")
        return redirect("exam_schedule")

    return redirect("exam_schedule")

def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    departments = Department.objects.all()

    if request.method == "POST":
        exam.subject_code = request.POST.get("subject_code")
        exam.subject_name = request.POST.get("subject_name")
        dept_id = request.POST.get("department")
        exam.department = Department.objects.get(id=dept_id)
        exam.date = request.POST.get("date")
        exam.time = request.POST.get("time")
        h, m, s = map(int, request.POST.get("duration").split(":"))
        exam.duration = timedelta(hours=h, minutes=m, seconds=s)
        exam.save()
        messages.success(request, f"Exam '{exam.subject_name}' updated successfully!")
        return redirect("exam_schedule")
    return redirect("exam_schedule")


def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    exam_name = exam.subject_name
    exam.delete()
    messages.success(request, f"Exam '{exam_name}' deleted successfully!")
    return redirect("exam_schedule")


def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    print(student)
    student.delete()
    messages.success(request, "Student deleted successfully ✅")
    return redirect('student_management')  
    
