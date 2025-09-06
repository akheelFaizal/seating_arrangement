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
    student = request.user.student  # Adjust if your auth model differs

    seatings = (
        Seating.objects
        .select_related('exam__course', 'exam__session', 'room')
        .filter(student=student)
        .order_by('exam__session__date', 'exam__session__time')
    )

    next_exam_seating = seatings.filter(exam__session__date__gte=date.today()).first()

    

    context = {
        'student': student,
        'seatings': seatings,
        'next_exam': next_exam_seating,
        # 'announcements': announcements,
        'today': date.today(),
    }

    return render(request, 'student/SeatView.html', context)


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

    # Fetch all rooms
    rooms = Room.objects.prefetch_related('seating_set__exam__session', 'seating_set__student').all()

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

#invigilator 


def teacheroverview(request):
    return render(request, 'invigilator/teachersoverview.html')


def add_exam(request):
    departments = Department.objects.all()
    sessions = ExamSession.objects.all()

    if request.method == "POST":
        subject_code = request.POST.get("subject_code")
        subject_name = request.POST.get("subject_name")
        department_id = request.POST.get("department")
        session_id = request.POST.get("session")

        department = Department.objects.get(id=department_id)
        session = ExamSession.objects.get(id=session_id)

        Exam.objects.create(
            subject_code=subject_code,
            subject_name=subject_name,
            department=department,
            session=session
        )

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

        # Update department
        dept_id = request.POST.get("department")
        if dept_id:
            exam.department = Department.objects.get(id=dept_id)

        # Update session
        session_id = request.POST.get("session")
        if session_id:
            exam.session = ExamSession.objects.get(id=session_id)

        exam.save()
        messages.success(request, f"Exam '{exam.subject_name}' updated successfully!")
        return redirect("exam_schedule")

    context = {
        "exam": exam,
        "departments": departments,
        "sessions": sessions,
    }
    return render(request, "admin/edit_exam.html", context)

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

        # Get all exams for the selected date
        exams = Exam.objects.filter(session__date=exam_date)
        if exams.exists():
            # Delete all seat assignments for these exams
            Seating.objects.filter(exam__in=exams).delete()
            messages.success(request, f"All seat assignments removed for {exam_date}")
        else:
            messages.warning(request, f"No exams found on {exam_date}")

    return redirect('seating_arrangement')


from datetime import date


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
        return redirect("room_management")

    # Get all rooms
    rooms = Room.objects.all().order_by("room_number")

    # Get selected date from GET
    selected_date = request.GET.get("date")
    if not selected_date:
        selected_date = date.today()

    # Attach seating queryset to each room
    for room in rooms:
        room.seatings_for_date = Seating.objects.filter(room=room, exam__session__date=selected_date)

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
        return redirect("room_management")

    return redirect("room_management")


def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    room.delete()
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

def news_reject(request, pk):
    news = get_object_or_404(NewsUpdate, pk=pk)
    news.status = "rejected"
    news.save()
    return redirect("news_updates")

from django.db.models import Count

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