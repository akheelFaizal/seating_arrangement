from django.db.models import Prefetch
from collections import defaultdict
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
from django.utils.timezone import now



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
    # Fetch all exams with related session info
    exams = Exam.objects.select_related('department', 'session').all().order_by('session__date')

    rooms = Room.objects.all()
    print(rooms)
    # Group exams by session date
    exams_by_date = defaultdict(list)
    for exam in exams:
        exams_by_date[exam.session.date].append(exam)

    # Convert to a sorted list of tuples (date, [exams])
    sorted_exams_by_date = sorted(exams_by_date.items())

    
    return render(request, 'admin/SeatingArrangement.html', {'exams_by_date': sorted_exams_by_date, 'rooms':rooms})


def ExamSchedule(request):
    departments = Department.objects.all()
    sessions = ExamSession.objects.all()  # Ensure sessions exist
    exams = Exam.objects.all().select_related('session', 'department')  # Efficient queries

    # Group exams by department
    dept_exams = defaultdict(list)
    for exam in exams:
        dept_exams[exam.department].append(exam)

    # Convert defaultdict to normal dict
    dept_exams = dict(dept_exams)

    context = {
        'departments': departments,
        'sessions': sessions,
        'dept_exams': dept_exams
    }
    return render(request, 'admin/ExamSchedule.html', context)


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
        rows = request.POST.get('rows')
        cols = request.POST.get('columns')
        capacity = int(rows) * int(cols) * 2
        Room.objects.create(room_number=room_number, capacity=capacity, rows=rows, columns=cols)
        messages.success(request, f"Room {room_number} added successfully!")   
    
    return redirect("seating_arrangement")


def assign_seats_by_date(request):
    if request.method == "POST":
        date = request.POST.get('date')
        exams = Exam.objects.filter(session__date=date)
        rooms = list(Room.objects.filter(status='active'))

        if not exams:
            messages.error(request, f"No exams scheduled on {date}.")
            return redirect('seating_arrangement')
        if not rooms:
            messages.error(request, "No active rooms available.")
            return redirect('seating_arrangement')

        for exam in exams:
            # Clear old seating for this exam
            Seating.objects.filter(exam=exam).delete()

            # Fetch students only for this exam’s department
            students = list(
                Student.objects.filter(
                    course__department=exam.department
                ).order_by('roll_number')
            )

            print(f"Exam: {exam.subject_name}, Dept: {exam.department}, Students: {len(students)}")

            # Group students by (course, dept, year)
            class_groups = defaultdict(list)
            for student in students:
                class_groups[(student.course, student.department, student.year)].append(student)

            # Round-robin distribution (interleave groups)
            distributed_students = []
            while any(class_groups.values()):
                for key in list(class_groups.keys()):
                    if class_groups[key]:
                        distributed_students.append(class_groups[key].pop(0))

            # Shuffle once for randomness
            random.shuffle(distributed_students)

            # Seat assignment
            student_index = 0
            for room in rooms:
                bench = []
                for seat_number in range(1, room.capacity + 1):
                    if student_index >= len(distributed_students):
                        break

                    student = distributed_students[student_index]

                    # Prevent consecutive same group on same bench
                    if bench and (
                        bench[-1].course == student.course and
                        bench[-1].department == student.department and
                        bench[-1].year == student.year
                    ):
                        swap_index = student_index + 1
                        while swap_index < len(distributed_students):
                            next_student = distributed_students[swap_index]
                            if (
                                bench[-1].course != next_student.course or
                                bench[-1].department != next_student.department or
                                bench[-1].year != next_student.year
                            ):
                                # Swap them
                                distributed_students[student_index], distributed_students[swap_index] = \
                                    distributed_students[swap_index], distributed_students[student_index]
                                student = distributed_students[student_index]
                                break
                            swap_index += 1
                        # if no swap found, assign anyway

                    # Create seating record
                    Seating.objects.create(
                        student=student,
                        exam=exam,
                        room=room,
                        seat_number=seat_number
                    )

                    bench.append(student)
                    if len(bench) == room.bench_capacity:
                        bench = []  # reset for new bench

                    student_index += 1

        messages.success(request, f"Seats assigned for all exams on {date}")
    return redirect('seating_arrangement')


<<<<<<< HEAD




#invigilator 

def teacheroverview(request):
    return render(request, 'invigilator/teachersoverview.html')

  
  
=======
>>>>>>> 433179d6439f24382fc1db689127f88a7426a0b4

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
    
def seating_map_detail(request, room_id):
    room = Room.objects.get(id=room_id)
    seats = list(Seating.objects.filter(room=room).order_by('seat_number'))

    benches = []
    bench_capacity = 2  # 2 students per bench

    seat_index = 0
    total_seats = len(seats)
    
    # Generate layout row by row, column by column
    for r in range(room.rows):
        row_benches = []
        for c in range(room.columns):
            bench = []
            for b in range(bench_capacity):
                if seat_index < total_seats:
                    student = seats[seat_index].student
                    bench.append({
                        'name': student.name,
                        'roll_number': student.roll_number,
                        'course': student.course,
                        'department': student.department,
                        'year': student.year
                    })
                    seat_index += 1
                else:
                    bench.append(None)  # empty seat
            row_benches.append(bench)
        benches.append(row_benches)

    context = {
        'room': room,
        'benches': benches,  # benches[row][column] = list of 2 students or None
        'bench_capacity': bench_capacity
    }
    return render(request, 'admin/seating_map_detail.html', context)


def remove_all_assignments(request):
    if request.method == "POST":
        date_str = request.POST.get('date')
        try:
            exam_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date format.")
            return redirect('seating_arrangement')

        exams = Exam.objects.filter(session__date=exam_date)
        if exams.exists():
            Seating.objects.filter(exam__in=exams).delete()
            messages.success(request, f"All seat assignments removed for {exam_date}")
        else:
            messages.warning(request, f"No exams found on {exam_date}")

    return redirect('seating_arrangement')