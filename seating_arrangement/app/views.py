from collections import defaultdict
from datetime import datetime
from datetime import datetime, date, timedelta
from django.core.mail import send_mail

import csv
import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from .models import *   
from django.db.models import Count

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.core.files.storage import default_storage


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")  # roll number / employee ID / admin username
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Save user info in session
            request.session["user_id"] = user.id
            request.session["role"] = user.role

            # ✅ Redirect based on role
            if user.role == "student":
                return redirect("student_overview")      # your student dashboard
            elif user.role == "invigilator":
                return redirect("invigilatordashboard")  # your invigilator dashboard
            elif user.role == "admin":
                return redirect("index")       # your admin dashboard
            else:
                messages.error(request, "Role not recognized.")
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "student/studentLogin.html")



def student_logout(request):
    logout(request)
    return redirect('login')  # Replace with your login URL name


def index(request):
    total_students = Student.objects.count()
    total_rooms = Room.objects.count()

    # Join exam with its session
    upcoming_exams = Exam.objects.filter(
        session__date__gte=now().date()
    ).order_by("session__date", "session__start_time")[:3]

    active_exams = upcoming_exams.count()  # could be refined by time window

    # Occupancy rate (dummy logic - adjust to your seating model)
    total_capacity = sum(room.capacity for room in Room.objects.all())
    used_capacity = total_capacity - sum(room.available_seats() for room in Room.objects.all()) if total_capacity else 0
    occupancy_rate = round((used_capacity / total_capacity) * 100, 2) if total_capacity else 0

    rooms = Room.objects.all()

    return render(request, "admin/Admin.html", {
        "total_students": total_students,
        "total_rooms": total_rooms,
        "active_exams": active_exams,
        "occupancy_rate": occupancy_rate,
        "upcoming_exams": upcoming_exams,
        "rooms": rooms,
    })





@login_required
def StudentOverView(request):
    # Get the student_id from session (CustomUser ID)
    student_id = request.session.get("user_id")

    if not student_id:
        return redirect("login")

    try:
        # Get the logged-in user
        custom_user = CustomUser.objects.get(id=student_id)
    except CustomUser.DoesNotExist:
        return redirect("login")

    # Try to fetch matching Student record
    student_data = None
    try:
        student_data = Student.objects.get(roll_number=custom_user.username)
    except Student.DoesNotExist:
        student_data = None

    # Fetch seatings
    seatings = (
        Seating.objects.filter(student=student_data)
        .select_related("exam", "exam__session", "room")
        .order_by("exam__session__date", "exam__session__start_time")
    )

    # Convert seatings into list of dicts for easy template rendering
    exam_seats = [
        {
            "exam_name": s.exam.subject_name,
            "seat_number": s.seat_number,
            "room_number": s.room.room_number,
        }
        for s in seatings
    ]

    # Fetch announcements
    announcements = NewsUpdate.objects.filter(status="approved").order_by("-created_at")

    context = {
        "user": custom_user,
        "student": student_data,
        "exam_seats": exam_seats,   # 👈 this matches your HTML
        "announcements": announcements,
        "hall_ticket_url": "#",     # placeholder (replace with actual)
    }
    return render(request, "student/studentOverView.html", context)


@login_required
def StudentSeatview(request):
    # Get the logged-in student based on roll number
    student = get_object_or_404(Student, roll_number=request.user.username)

    # Fetch all seatings for this student
    seatings = (
    Seating.objects.filter(student=student)
    .select_related("exam", "exam__session", "room")
    .order_by("exam__session__date", "exam__session__start_time")
    )

    # Next upcoming exam
    next_exam = (
        seatings.filter(exam__session__date__gte=date.today())
        .order_by("exam__session__date", "exam__session__start_time")
        .first()
    )

    # Announcements (replace with DB model if available)
    announcements = NewsUpdate.objects.filter(status='approved').order_by('-created_at')

    context = {
        "student": student,
        "seatings": seatings,
        "next_exam": next_exam,
        "announcements": announcements,
        "today": date.today(),
        "hall_ticket_url": "#",  # Replace with actual hall ticket link if available
    }
    return render(request, "student/StudentSeatView.html", context)


def StudentResultView(request):
    return render(request, 'student/studentResultView.html')


def StudentExamDetail(request):
    # Get logged-in student
    student = get_object_or_404(Student, roll_number=request.user.username)

    # Fetch seatings (exams for this student)
    seatings = (
        Seating.objects.filter(student=student)
        .select_related("exam", "exam__session", "room")
        .order_by("exam__session__date", "exam__session__start_time")
    )

    # Next upcoming exam
    next_exam = seatings.first()
    announcements = NewsUpdate.objects.filter(status='approved').order_by('-created_at')
    context = {
        "student": student,
        "seatings": seatings,
        "next_exam": next_exam,
        "announcements": announcements
    }
    return render(request, "student/StudentExamDetail.html", context)


#admin


def StudentManagement(request):
    departments = Department.objects.all()
    courses = Course.objects.all()

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
        "courses": courses,
        "students": students,
        "selected_dept": dept_filter,
        "selected_year": year_filter,
        "search_query": search_query,
    })


def bulk_delete_students(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_students")
        if ids:
            Student.objects.filter(id__in=ids).delete()
            messages.success(request, f"Deleted {len(ids)} students successfully.")
        else:
            messages.warning(request, "No students selected.")
    return redirect("student_management") 

def SeatingArrangement(request):
    # Fetch all exams with related session info
    exams = Exam.objects.select_related('session').prefetch_related('department').all().order_by('session__date')

    # Fetch all rooms
    rooms = Room.objects.prefetch_related(
        Prefetch(
            'seating_set',  # reverse relation from Room → Seating
            queryset=Seating.objects.select_related('student', 'examSession')
        )
    )
    # Group exams by session date
    exams_by_date = defaultdict(list)
    for exam in exams:
        exams_by_date[exam.session.date].append(exam)
    sorted_exams_by_date = sorted(exams_by_date.items())

    # Group room seating by date for JS filter
    rooms_by_date = defaultdict(list)
    for room in rooms:
        # Check each seat in the room
        seat_dates = set()
        for seat in room.seating_set.all():
            seat_dates.add(seat.exam.session.date)
        for date in seat_dates:
            rooms_by_date[date].append(room)

    return render(request, 'admin/SeatingArrangement.html', {
        'exams_by_date': sorted_exams_by_date,
        'rooms': rooms,
        'rooms_by_date': rooms_by_date,  # optional, for server-side filtering if needed
    })


def ExamSchedule(request):
    departments = Department.objects.all()
    sessions = ExamSession.objects.all()
    
    exams = Exam.objects.all().prefetch_related('department', 'session')
    print(f"Total exams found: {exams.count()}")  # ✅ Debug: number of exams

    # Group exams by department
    dept_exams = defaultdict(list)
    for exam in exams:
        dept_list = list(exam.department.all())
        print(f"Exam: {exam.subject_name}, Departments: {[d.name for d in dept_list]}")  # ✅ Debug: which depts each exam belongs to
        for dept in dept_list:
            dept_exams[dept].append(exam)

    print(f"Departments with exams: {[d.name for d in dept_exams.keys()]}")  # ✅ Debug: which departments have exams

    context = {
        'departments': departments,
        'sessions': sessions,
        'dept_exams': dict(dept_exams)
    }
    return render(request, 'admin/ExamSchedule.html', context)
# functionalities   

# def upload_students(request):
#     if request.method == "POST" and request.FILES.getlist("files"):
#         files = request.FILES.getlist("files")
        
#         for csv_file in files:
#             decoded_file = csv_file.read().decode("utf-8").splitlines()
#             reader = csv.DictReader(decoded_file)
            
#             for row in reader:
#                 dept, _ = Department.objects.get_or_create(name=row['Department'])
#                 course, _ = Course.objects.get_or_create(name=row['Course'], department=dept)
#                 Student.objects.update_or_create(
#                     roll_number=row['Roll Number'],
#                     defaults={
#                         'name': row['Name'],
#                         'department': dept,
#                         'course': course
#                     }
#                 )
#         messages.success(request, "All student files uploaded successfully!")  
#     else:
#         messages.error(request, "No files were selected for upload!")          
    
#     return redirect("seating_arrangement")
def upload_students(request):
    if request.method == "POST" and request.FILES.getlist("files"):
        files = request.FILES.getlist("files")

        for csv_file in files:
            # Decode with utf-8-sig to remove BOM
            decoded_file = csv_file.read().decode("utf-8-sig").splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                # Clean up extra spaces just in case
                row = {k.strip(): v.strip() for k, v in row.items()}

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


# def assign_seats_by_date(request):
#     if request.method == "POST":
#         date = request.POST.get('date')
#         exams = Exam.objects.filter(session__date=date)
#         rooms = list(Room.objects.filter(status='active'))

#         if not exams:
#             messages.error(request, f"No exams scheduled on {date}.")
#             return redirect('seating_arrangement')
#         if not rooms:
#             messages.error(request, "No active rooms available.")
#             return redirect('seating_arrangement')

#         for exam in exams:
#             # Clear old seating for this exam
#             Seating.objects.filter(exam=exam).delete()

#             # Fetch students only for this exam’s department
#             departments = exam.department.all()  # queryset of departments
#             students = list(
#                     Student.objects.filter(
#                         course__department__in=departments
#                     ).order_by('roll_number')
#                 )

#             print(f"Exam: {exam.subject_name}, Dept: {exam.department}, Students: {len(students)}")

#             # Group students by (course, dept, year)
#             class_groups = defaultdict(list)
#             for student in students:
#                 class_groups[(student.course, student.department, student.year)].append(student)

#             # Round-robin distribution (interleave groups)
#             distributed_students = []
#             while any(class_groups.values()):
#                 for key in list(class_groups.keys()):
#                     if class_groups[key]:
#                         distributed_students.append(class_groups[key].pop(0))

#             # Shuffle once for randomness
#             random.shuffle(distributed_students)

#             # Seat assignment
#             student_index = 0
#             for room in rooms:
#                 bench = []
#                 for seat_number in range(1, room.capacity + 1):
#                     if student_index >= len(distributed_students):
#                         break

#                     student = distributed_students[student_index]

#                     # Prevent consecutive same group on same bench
#                     if bench and (
#                         bench[-1].course == student.course and
#                         bench[-1].department == student.department and
#                         bench[-1].year == student.year
#                     ):
#                         swap_index = student_index + 1
#                         while swap_index < len(distributed_students):
#                             next_student = distributed_students[swap_index]
#                             if (
#                                 bench[-1].course != next_student.course or
#                                 bench[-1].department != next_student.department or
#                                 bench[-1].year != next_student.year
#                             ):
#                                 # Swap them
#                                 distributed_students[student_index], distributed_students[swap_index] = \
#                                     distributed_students[swap_index], distributed_students[student_index]
#                                 student = distributed_students[student_index]
#                                 break
#                             swap_index += 1
#                         # if no swap found, assign anyway

#                     # Create seating record
#                     Seating.objects.create(
#                         student=student,
#                         exam=exam,
#                         room=room,
#                         seat_number=seat_number
#                     )

#                     bench.append(student)
#                     if len(bench) == room.bench_capacity:
#                         bench = []  # reset for new bench

#                     student_index += 1

#         messages.success(request, f"Seats assigned for all exams on {date}")
#     return redirect('seating_arrangement')


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

        total_room_capacity = sum(room.capacity for room in rooms)

        for exam in exams:
            # Fetch students for exam's department
            departments = exam.department.all()
            students = list(
                Student.objects.filter(
                    course__department__in=departments
                ).order_by('roll_number')
            )

            print(f"Exam: {exam.subject_name}, Departments: {departments}, Students: {len(students)}")

            # ✅ Check if total students exceed available seats
            if len(students) > total_room_capacity:
                messages.error(
                    request,
                    f"Room capacity exceeded for exam '{exam.subject_name}'. "
                    f"Total students: {len(students)}, Available seats: {total_room_capacity}."
                )
                return redirect('seating_arrangement')

            # Clear old seating for this exam
            Seating.objects.filter(exam=exam).delete()

            # Group students by (course, dept, year)
            class_groups = defaultdict(list)
            for student in students:
                class_groups[(student.course, student.department, student.year)].append(student)

            # Round-robin distribution
            distributed_students = []
            while any(class_groups.values()):
                for key in list(class_groups.keys()):
                    if class_groups[key]:
                        distributed_students.append(class_groups[key].pop(0))

            random.shuffle(distributed_students)

            # Start assigning seats
            student_index = 0
            for room in rooms:
                bench = []
                for seat_number in range(1, room.capacity + 1):
                    if student_index >= len(distributed_students):
                        break

                    student = distributed_students[student_index]

                    # Prevent consecutive same group on the same bench
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
                                distributed_students[student_index], distributed_students[swap_index] = \
                                    distributed_students[swap_index], distributed_students[student_index]
                                student = distributed_students[student_index]
                                break
                            swap_index += 1

                    Seating.objects.create(
                        student=student,
                        exam=exam,
                        room=room,
                        seat_number=seat_number
                    )

                    bench.append(student)
                    if len(bench) == room.bench_capacity:
                        bench = []
                    student_index += 1

        messages.success(request, f"Seats assigned for all exams on {date}")
    return redirect('seating_arrangement')



def debarmanagement(request):
    # Base queryset
    students = Student.objects.all().select_related("course", "department", "debarred_by")
    rooms = Room.objects.all()

    # Search
    search_query = request.GET.get("search", "")
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(roll_number__icontains=search_query)
        )

    # Filters
    course_filter = request.GET.get("course", "")
    dept_filter = request.GET.get("department", "")
    year_filter = request.GET.get("year", "")
    debarred_filter = request.GET.get("debarred", "")

    if course_filter:
        students = students.filter(course__id=course_filter)
    if dept_filter:
        students = students.filter(department__id=dept_filter)
    if year_filter:
        students = students.filter(year=year_filter)
    if debarred_filter == "yes":
        students = students.filter(is_debarred=True)
    elif debarred_filter == "no":
        students = students.filter(is_debarred=False)

    if request.method == "POST":
        # 🔄 Update all seats + rooms
        if "update_all_seats" in request.POST:
            updated_count = 0
            for key, value in request.POST.items():
                if key.startswith("seat_") or key.startswith("room_"):
                    roll_number = key.split("_", 1)[1]
                    student = get_object_or_404(Student, roll_number=roll_number)

                    seating, _ = Seating.objects.get_or_create(student=student, exam=Exam.objects.first())

                    if key.startswith("seat_") and value.strip() and seating.seat_number != value.strip():
                        seating.seat_number = value.strip()
                        updated_count += 1

                    if key.startswith("room_") and value:
                        try:
                            room = Room.objects.get(room_number=value)
                            if seating.room != room:
                                seating.room = room
                                updated_count += 1
                        except Room.DoesNotExist:
                            continue

                    seating.save()

            messages.success(request, f"Seats/rooms updated for {updated_count} students.")
            return redirect("debar-management")

        # 🚫 Single student debar
        for key in request.POST:
            if key.startswith("debar_"):
                roll_number = key.replace("debar_", "")
                student = get_object_or_404(Student, roll_number=roll_number)
                student.is_debarred = True
                student.debarred_by = request.user  # Track who debarred
                student.save()
                messages.warning(request, f"{student.name} has been debarred!")
                return redirect("debar-management")

    # Only pass students who are debarred for the template section
    debarred_students = students.filter(is_debarred=True)

    return render(request, 'admin/debarmanagement.html', {
        "students": students,
        "debarred_students": debarred_students,
        "rooms": rooms,
        "courses": Course.objects.all(),
        "departments": Department.objects.all(),
        "years": [1, 2, 3, 4],
        "search_query": search_query,
        "course_filter": course_filter,
        "dept_filter": dept_filter,
        "year_filter": year_filter,
        "debarred_filter": debarred_filter,
    })


#invigilator 


def teacheroverview(request):
    return render(request, 'invigilator/teachersoverview.html')

def add_exam(request):
    departments = Department.objects.all()
    sessions = ExamSession.objects.all()

    if request.method == "POST":
        subject_code = request.POST.get("subject_code")
        subject_name = request.POST.get("subject_name")
        department_ids = request.POST.getlist("department")  # ✅ getlist for multiple selection
        session_id = request.POST.get("session")

        session = ExamSession.objects.get(id=session_id)

        # Create exam first (without departments)
        exam = Exam.objects.create(
            subject_code=subject_code,
            subject_name=subject_name,
            session=session
        )

        # Assign multiple departments
        exam.department.set(department_ids)

        messages.success(request, f"Exam '{subject_name}' added successfully!")
        return redirect("exam_schedule")

    return render(request, "add_exam.html", {
        "departments": departments,
        "sessions": sessions
    })


def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    departments = Department.objects.all()
    sessions = ExamSession.objects.all()  # for session dropdown

    if request.method == "POST":
        exam.subject_code = request.POST.get("subject_code")
        exam.subject_name = request.POST.get("subject_name")

        # Update departments (many-to-many)
        dept_ids = request.POST.getlist("department")  # getlist for multiple selection
        if dept_ids:
            exam.department.set(Department.objects.filter(id__in=dept_ids))  # update M2M
        else:
            exam.department.clear()  # if no department selected, clear all

        # Update session (ForeignKey)
        session_id = request.POST.get("session")
        if session_id:
            exam.session = ExamSession.objects.get(id=session_id)

        exam.save()
        messages.success(request, f"Exam '{exam.subject_name}' updated successfully!")
        return redirect("exam_schedule")
    return redirect("exam_schedule")

   
def delete_exam(request, exam_id, department_id):
    exam = get_object_or_404(Exam, id=exam_id)
    department = get_object_or_404(Department, id=department_id)

    # Remove the connection between exam and department
    exam.department.remove(department)
    messages.success(request, f"Department '{department.name}' removed from exam '{exam.subject_name}' successfully!")

    # If exam has no more departments, delete the exam itself
    if exam.department.count() == 0:
        exam_name = exam.subject_name
        exam.delete()
        messages.success(request, f"Exam '{exam_name}' deleted as it has no more departments connected!")

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
    bench_capacity = 1  # 2 students per bench

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

        # Get all exams for the selected date
        exams = Exam.objects.filter(session__date=exam_date)
        if exams.exists():
            # Delete all seat assignments for these exams
            Seating.objects.filter(exam__in=exams).delete()
            messages.success(request, f"All seat assignments removed for {exam_date}")
        else:
            messages.warning(request, f"No exams found on {exam_date}")

    return redirect('seating_arrangement')


def room_management(request):
    # Handle Add Room
    if request.method == "POST":
        room_number = request.POST.get("room_number")
        rows = int(request.POST.get("rows", 0))
        columns = int(request.POST.get("columns", 0))
        capacity = rows * columns
        Room.objects.create(
            room_number=room_number,
            rows=rows,
            columns=columns,
            capacity=capacity
        )
        messages.success(request, f"Room {room_number} added successfully with capacity {capacity}!")

        return redirect("room_management")

    # Get all rooms
    rooms = Room.objects.all().order_by("room_number")

    # Get selected date from GET
    selected_date = request.GET.get("date")
    if not selected_date:
        selected_date = date.today()

    # Attach seating queryset to each room
    for room in rooms:
        room.seatings_for_date = Seating.objects.filter(room=room, examSession__date=selected_date)

    context = {
        "rooms": rooms,
        "today": date.today(),
        "selected_date": selected_date
    }
    return render(request, "admin/RoomManagement.html", context)

def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == "POST":
        room.room_number = request.POST.get("room_number")
        room.rows = int(request.POST.get("rows", 0))
        room.columns = int(request.POST.get("columns", 0))
        room.capacity = room.rows * room.columns
        room.save()
        messages.success(request, f"Room '{room.room_number}' updated successfully!")
        return redirect("room_management")

    return redirect("room_management")


def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    room.delete()
    messages.error(request, f"Room '{room.room_number}' Deleted successfully!")
    return redirect("room_management")

def NewsManagement(request):
    if request.method == "POST":
        # Handle new post
        title = request.POST.get("title")
        content = request.POST.get("content")
        posted_by = request.POST.get("posted_by")
        status = "approved" if posted_by.lower() == "admin" else "pending"
        NewsUpdate.objects.create(title=title, content=content, posted_by=posted_by, status=status)
        return redirect("news_updates")

    # Fetch approved and pending news
    approved_news = NewsUpdate.objects.filter(status="approved").order_by('-created_at')
    pending_news = NewsUpdate.objects.filter(status="pending").order_by('-created_at')

    context = {
        "approved_news": approved_news,
        "pending_news": pending_news
    }
    return render(request, 'admin/Updates.html', context)

def news_approve(request, pk):
    news = get_object_or_404(NewsUpdate, pk=pk)
    news.status = "approved"
    news.save()
    return redirect("news_updates")

def delete_news(request, news_id):
    news = get_object_or_404(NewsUpdate, id=news_id)
    title = news.title
    news.delete()
    messages.success(request, f"News '{title}' has been deleted successfully!")
    return redirect(request.META.get("HTTP_REFERER", "admin_dashboard"))

def news_reject(request, pk):
    news = get_object_or_404(NewsUpdate, pk=pk)
    news.status = "rejected"
    news.save()
    return redirect("news_updates")

def analytics(request):
    # 1️⃣ Metrics
    total_students = Student.objects.count()
    total_rooms = Room.objects.count()
    total_exams = Exam.objects.count()
    
    # Pending Approvals → from NewsUpdate model
    pending_approvals = NewsUpdate.objects.filter(status="pending").count()

    # 2️⃣ Students per Department
    dept_data = (
        Student.objects.values('department__name')
        .annotate(count=Count('id'))
        .order_by('department__name')
    )
    departments = [d['department__name'] for d in dept_data]
    dept_counts = [d['count'] for d in dept_data]

    # 3️⃣ Exams per Date (group by ExamSession.date)
    exam_data = (
        Exam.objects.values('session__date')
        .annotate(count=Count('id'))
        .order_by('session__date')
    )
    exam_dates = [str(e['session__date']) for e in exam_data]
    exam_counts = [e['count'] for e in exam_data]

    # 4️⃣ Room Utilization (number of students assigned via Seating)
    room_data = (
        Room.objects.values('room_number')
        .annotate(count=Count('seating'))
        .order_by('room_number')
    )
    room_names = [r['room_number'] for r in room_data]
    room_counts = [r['count'] for r in room_data]

    context = {
        "total_students": total_students,
        "total_rooms": total_rooms,
        "total_exams": total_exams,
        "pending_approvals": pending_approvals,
        "departments": departments,
        "dept_counts": dept_counts,
        "exam_dates": exam_dates,
        "exam_counts": exam_counts,
        "room_names": room_names,
        "room_counts": room_counts,
    }

    return render(request, "admin/Analytics.html", context)

#invigilators
@login_required
def invigilator_dashboard(request):
    user = request.user

    # Only invigilators should access
    if getattr(user, 'role', None) != "invigilator":
        return redirect("login")  # or redirect to student dashboard

    # Fetch assigned room(s) for this invigilator
    assigned_rooms = Room.objects.filter(supervisor=user)
    
    # For simplicity, pick first room
    room = assigned_rooms.first() if assigned_rooms.exists() else None

    # Fetch students in that room
    students = Seating.objects.filter(room=room).select_related('student', 'exam') if room else []

    # Find next exam (nearest by date)
    next_exam = None
    if students:
        next_exam = students.order_by('exam__session__date').first().exam

    context = {
        "user": user,
        "room": room,
        "students": students,
        "next_exam": next_exam,
    }

    return render(request, 'invigilator/invigilatorOverview.html', context)

@login_required
def invigilatorSeatarrangement(request):
    # Base queryset
    students = Student.objects.all().select_related("course", "department")
    rooms = Room.objects.all()

    # Search
    search_query = request.GET.get("search", "")
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(roll_number__icontains=search_query)
        )

    # Filters
    course_filter = request.GET.get("course", "")
    dept_filter = request.GET.get("department", "")
    year_filter = request.GET.get("year", "")
    debarred_filter = request.GET.get("debarred", "")

    if course_filter:
        students = students.filter(course__id=course_filter)
    if dept_filter:
        students = students.filter(department__id=dept_filter)
    if year_filter:
        students = students.filter(year=year_filter)
    if debarred_filter == "yes":
        students = students.filter(is_debarred=True)
    elif debarred_filter == "no":
        students = students.filter(is_debarred=False)

    if request.method == "POST":
        # 🔄 Update all seats + rooms
        if "update_all_seats" in request.POST:
            updated_count = 0
            for key, value in request.POST.items():
                if key.startswith("seat_") or key.startswith("room_"):
                    roll_number = key.split("_", 1)[1]
                    student = get_object_or_404(Student, roll_number=roll_number)

                    # Get or create seating record
                    seating, _ = Seating.objects.get_or_create(
                        student=student, 
                        exam=Exam.objects.first(),
                        defaults={"seat_number": 0, "room": rooms.first()}
                    )

                    if key.startswith("seat_"):
                        seat_value = value.strip()
                        if seat_value and seating.seat_number != seat_value:
                            seating.seat_number = seat_value
                            updated_count += 1

                    if key.startswith("room_"):
                        if value:
                            room = Room.objects.get(room_number=value)
                            if seating.room != room:
                                seating.room = room
                                updated_count += 1

                    seating.save()

            messages.success(request, f"Seats/rooms updated for {updated_count} students.")
            return redirect("invigilatorseatarrangement")

        # 🚫 Debar single student
        for key in request.POST:
            if key.startswith("debar_"):
                roll_number = key.replace("debar_", "")
                student = get_object_or_404(Student, roll_number=roll_number)
                student.is_debarred = True
                student.debarred_by = request.user
                student.save()
                messages.warning(request, f"{student.name} has been debarred!")
                return redirect("invigilatorseatarrangement")

    return render(request, 'invigilator/invigilatorSeatarrangement.html', {
        "students": students,
        "rooms": rooms,
        "courses": Course.objects.all(),
        "departments": Department.objects.all(),
        "years": [1, 2, 3, 4],
        "search_query": search_query,
        "course_filter": course_filter,
        "dept_filter": dept_filter,
        "year_filter": year_filter,
        "debarred_filter": debarred_filter,
    })

@login_required
def invigilatorProfile(request):
    user = request.user

    # Ensure only invigilators can access
    if getattr(user, 'role', None) != "invigilator":
        return redirect("login")  # or student dashboard

    # Assigned room (if any)
    room = Room.objects.filter(supervisor=user).first()

    # Students in that room (optional)
    students = Seating.objects.filter(room=room).select_related("student", "exam") if room else []

    # Upcoming exams assigned to this invigilator (from Seating)
    upcoming_invigilations = []
    if students:
        for seat in students:
            upcoming_invigilations.append({
                "date": seat.exam.session.date,
                "time": seat.exam.session.start_time,
                "subject": seat.exam.subject_name,
                "room": seat.room.room_number
            })
        # Sort by date and time
        upcoming_invigilations.sort(key=lambda x: (x['date'], x['time']))

    context = {
        "user": user, 
        "invigilator": {
            "invigilator_id": user.id,
            "full_name": user.name,
            "department": user.invigilator_department if user.invigilator_department else "N/A",
            "room_allotted": room.room_number if room else "-",
            "next_exam": students.order_by('exam__session__date').first().exam.subject_name if students else "-",
            
        },
        "upcoming_invigilations": upcoming_invigilations
    }

    return render(request, "invigilator/invigilatorProfile.html", context)


def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")
        roll_number = request.POST.get("roll_number")
        course_id = request.POST.get("course")
        department_id = request.POST.get("department")
        year = request.POST.get("year")

        # Prevent duplicate roll numbers
        if CustomUser.objects.filter(username=roll_number).exists():
            messages.error(request, "Roll number already registered.")
            return redirect("signup")

        # Get related course and department
        course_obj = Course.objects.get(id=course_id)
        dept_obj = Department.objects.get(id=department_id)

        # ✅ Create student user
        user = CustomUser.objects.create_user(
            username=roll_number,
            first_name=name,
            role="student",
            course=course_obj,
            department=dept_obj,
            year=year,
            password=password,
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    # GET request
    courses = Course.objects.all()
    departments = Department.objects.all()
    return render(request, "student/studentSignup.html", {
        "courses": courses,
        "departments": departments,
    })



@login_required
def edit_invigilator_profile(request):
    user = request.user

    # Only invigilators can access
    if getattr(user, "role", None) != "invigilator":
        return redirect("login")

    if request.method == "POST":
        name = request.POST.get("name")
        department = request.POST.get("department")
        profile_picture = request.FILES.get("profile_picture")

        if name:
            user.name = name
        if department:
            user.invigilator_department = department
        if profile_picture:
            user.profile_picture = profile_picture

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("invigilatorprofile")

    return render(request, "invigilator/editProfile.html", {
        "user": user,
    })


# def invigilator_management(request):
#     # Prefetch rooms in a single query using select_related or annotate
#     invigilators = CustomUser.objects.filter(role="invigilator").select_related()
#     debarred_students = Student.objects.filter(is_debarred=True)

#     # Get all rooms with supervisors in one query
#     rooms = Room.objects.select_related('supervisor').all()
#     allrooms = Room.objects.all()
#     print(allrooms)
#     room_map = {room.supervisor_id: room.room_number for room in rooms if room.supervisor_id}

#     # Prepare data for template
#     data = [
#         {
#             'id': inv.id,
#             'name': inv.name ,
#             'username': inv.username,
#             'email': inv.email,
#             'phone': inv.phone,  # or a phone field if available
#             'assigned_room': room_map.get(inv.id)
#         }
#         for inv in invigilators
#     ]

#     return render(request, 'admin/InvigilatorManagement.html', {'invigilators': data, 'rooms': allrooms, 'debarred_students':debarred_students})

def invigilator_management(request):
    # Invigilator data
    invigilators = CustomUser.objects.filter(role="invigilator").select_related()
    debarred_students = Student.objects.filter(is_debarred=True)

    # Student data
    students = CustomUser.objects.filter(role="student").select_related('department', 'course')

    # Get all rooms with supervisors in one query
    rooms = Room.objects.select_related('supervisor').all()
    allrooms = Room.objects.all()

    # Map supervisor_id → room_number
    room_map = {room.supervisor_id: room.room_number for room in rooms if room.supervisor_id}

    # Prepare invigilator data for template
    invigilator_data = [
        {
            'id': inv.id,
            'name': inv.name,
            'username': inv.username,
            'email': inv.email,
            'phone': inv.phone,
            'assigned_room': room_map.get(inv.id)
        }
        for inv in invigilators
    ]

    # Prepare student data for template
    student_data = [
        {
            'id': stu.id,
            'name': stu.first_name,
            'username': stu.username,
            'email': stu.email,
            'phone': stu.phone,
            'department': stu.department.name if stu.department else None,
            'course': stu.course.name if stu.course else None,
            'year': stu.year
        }
        for stu in students
    ]

    return render(request, 'admin/InvigilatorManagement.html', {
        'invigilators': invigilator_data,
        'students': student_data,
        'rooms': allrooms,
        'debarred_students': debarred_students
    })


def add_session(request):
    if request.method == "POST":
        date = request.POST.get('date')
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')
        if (date and start and end) :
            ExamSession.objects.create(date=date, start_time=start, end_time=end)
            messages.success(request, "Session created successfully.")
            return redirect('exam_schedule')
        messages.error(request, "Fill all the fields.")
        return redirect('exam_schedule')
  
def add_invigilator(request):
    if request.method == "POST":
        username = request.POST.get("username")
        emp_id = request.POST.get("eid")
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        department = request.POST.get("department")

        if email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, "An invigilator with this email already exists.")
        else:
            invigilator = CustomUser.objects.create(
                username=username,
                employee_id=emp_id,
                first_name=name,
                email=email,
                phone=phone,
                role="invigilator",
                invigilator_department=department,
            )
            invigilator.set_password(password)  # use form password
            invigilator.save()
            messages.success(request, "Invigilator added successfully.")

            send_invigilator_credentials(email, username, password)

        
        return redirect("invigilator_management")
        

def assign_invigilator_room(request, invigilator_id):
    invigilator = get_object_or_404(CustomUser, id=invigilator_id, role="invigilator")

    if request.method == "POST":
        room_id = request.POST.get("room")
        if room_id:
            room = get_object_or_404(Room, id=room_id)
            # Remove invigilator from any previous room
            Room.objects.filter(supervisor=invigilator).update(supervisor=None)
            # Assign to selected room
            room.supervisor = invigilator
            room.save()
            messages.success(request, f"{invigilator.name} assigned to {room.room_number}.")
        return redirect("invigilator_management")
    
def reinstate_student(request, id):
    student = get_object_or_404(Student, id=id)

    if student.is_debarred:
        student.is_debarred = False
    else:
        student.is_debarred = True
    student.save()
    return redirect('invigilator_management')

from django.core.mail import send_mail
from django.conf import settings

def send_invigilator_credentials(email, username, password):
    subject = "Your Invigilator Account Credentials"
    message = f"""
    Dear {username},

    Your invigilator account has been created successfully.

    Login details:
    Username: {username}
    Password: {password}

    Please log in and change your password after first login.
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


@login_required
def invigilatorAssignedStudents(request):
        user = request.user
        # Ensure user is an invigilator
        if user.role != "invigilator":
            messages.error(request, "Access denied. Only invigilators can access this page.")
            return redirect("login")

        # Get the room assigned to this invigilator
        try:
            room = Room.objects.get(supervisor=user)
        except Room.DoesNotExist:
            room = None

        students = []
        if room:
            students = Seating.objects.filter(room=room).select_related("student", "exam")

            # Optional search filter by student name or roll number
            query = request.GET.get("search")
            if query:
                students = students.filter(student__name__icontains=query) | students.filter(student__roll_number__icontains=query)

        context = {
            "user": user,
            "room": room,
            "students": students,
        }
        return render(request, "invigilator/assignedstudent.html", context)



def edit_student(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        student = get_object_or_404(Student, id=student_id)

        # Update fields
        student.roll_number = request.POST.get("roll_number")
        student.name = request.POST.get("name")

        dept_id = request.POST.get("department")
        course_id = request.POST.get("course")
        year = request.POST.get("year")
        is_debarred = request.POST.get("is_debarred")

        if dept_id:
            student.department = get_object_or_404(Department, id=dept_id)
        if course_id:
            student.course = get_object_or_404(Course, id=course_id)
        if year:
            student.year = int(year)

        student.is_debarred = True if is_debarred else False

        student.save()

        messages.success(request, "Student details updated successfully ✅")
        return redirect("student_management")  # <-- replace with your main student list view name

    messages.error(request, "Invalid request ❌")
    return redirect("student_management")

def student_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        department_id = request.POST.get("department")
        course_id = request.POST.get("course")
        year = request.POST.get("year")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect('user_management')

        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, "Username already exists.")
            return redirect('user_management')

        if email and CustomUser.objects.filter(email=email).exists():
            messages.warning(request, "Email already exists.")
            return redirect('user_management')

        department = Department.objects.filter(id=department_id).first() if department_id else None
        course = Course.objects.filter(id=course_id).first() if course_id else None

        CustomUser.objects.create(
            name=name,
            username=username,
            email=email,
            phone=phone,
            password=make_password(password),
            department=department,
            course=course,
            year=year or None,
            role="student"
        )

        messages.success(request, f"Student '{name}' added successfully!")
        return redirect('user_management')

    return redirect('user_management')

def delete_invigilator(request, id):
    if request.method == "POST":
        invigilator = get_object_or_404(CustomUser, id=id, role="invigilator")
        invigilator.delete()
        messages.success(request, "Invigilator deleted successfully.")
    return redirect("invigilator_management")

def delete_student_user(request, id):
    if request.method == "POST":
        student = get_object_or_404(CustomUser, id=id, role="student")
        student.delete()
    messages.success(request, "Student deleted successfully.")
    return redirect("invigilator_management")

