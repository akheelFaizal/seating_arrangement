from django.shortcuts import render, redirect
from . models import *
from django.contrib import messages
import csv
import random


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

  
  

