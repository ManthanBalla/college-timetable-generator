import pandas as pd
import random
import os

# -----------------------------
# Load Data from CSV
# -----------------------------
def load_data():
    teachers_df = pd.read_csv("teachers.csv")
    classrooms_df = pd.read_csv("classrooms.csv")
    subjects_df = pd.read_csv("subjects.csv")
    labs_df = pd.read_csv("labs.csv")

    teachers = {row.Teacher_Name: row.Subjects.split(",") for _, row in teachers_df.iterrows()}
    classrooms = classrooms_df[classrooms_df["Type"] == "Classroom"]["Room_Name"].tolist()
    labs = labs_df["Lab_Name"].tolist()
    subjects_per_sem = {sem: group["Subject"].tolist() for sem, group in subjects_df.groupby("Semester")}

    return teachers, classrooms, labs, subjects_per_sem

# -----------------------------
# Slots & Days
# -----------------------------
slots = {
    1: "9:15-10:15",
    2: "10:15-11:15",
    3: "11:30-12:30",  # after morning break
    4: "12:30-1:30",
    5: "2:00-3:00",    # after lunch
    6: "3:00-4:00"
}
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# -----------------------------
# Helper Functions
# -----------------------------
def get_teacher_for_subject(subject, teachers):
    possible = [t for t, subs in teachers.items() if subject in subs]
    return random.choice(possible) if possible else None

def assign_lab(day, start_slot, sem, timetable, teacher_bookings, room_bookings, lab_bookings, teachers, labs, subjects_per_sem):
    subject = random.choice(subjects_per_sem[sem])
    teacher = get_teacher_for_subject(subject, teachers)
    lab_room = random.choice(labs)

    # Check for clashes
    if (teacher in teacher_bookings[day][start_slot] or
        teacher in teacher_bookings[day][start_slot + 1] or
        lab_room in room_bookings[day][start_slot] or
        lab_room in room_bookings[day][start_slot + 1] or
        lab_bookings[day][start_slot] or
        lab_bookings[day][start_slot + 1]):
        return False

    # Assign lab
    for s in [start_slot, start_slot + 1]:
        timetable[day][s] = f"{subject} (Lab)\n{teacher}\n{lab_room}"
        teacher_bookings[day][s].append(teacher)
        room_bookings[day][s].append(lab_room)
        lab_bookings[day][s] = True
    return True

def assign_lecture(day, slot, sem, timetable, teacher_bookings, room_bookings, teachers, classrooms, subjects_per_sem):
    subject = random.choice(subjects_per_sem[sem])
    teacher = get_teacher_for_subject(subject, teachers)
    room = random.choice(classrooms)

    if teacher in teacher_bookings[day][slot] or room in room_bookings[day][slot]:
        return False

    timetable[day][slot] = f"{subject}\n{teacher}\n{room}"
    teacher_bookings[day][slot].append(teacher)
    room_bookings[day][slot].append(room)
    return True

# -----------------------------
# Main Timetable Generation
# -----------------------------
def generate_timetable_for_semester(sem):
    teachers, classrooms, labs, subjects_per_sem = load_data()

    if sem not in subjects_per_sem:
        raise ValueError(f"No subjects found for {sem}")

    timetable = {day: {s: "" for s in slots.keys()} for day in days}
    teacher_bookings = {day: {s: [] for s in slots.keys()} for day in days}
    room_bookings = {day: {s: [] for s in slots.keys()} for day in days}
    lab_bookings = {day: {s: False for s in slots.keys()} for day in days}

    for day in days:
        # Randomly decide if lab will be assigned today
        lab_slots_start = [1, 3, 5]
        random.shuffle(lab_slots_start)
        for start in lab_slots_start:
            if random.choice([True, False]):
                if assign_lab(day, start, sem, timetable, teacher_bookings, room_bookings, lab_bookings, teachers, labs, subjects_per_sem):
                    break

        # Assign lectures in remaining slots
        for slot in slots.keys():
            if timetable[day][slot] == "":
                assign_lecture(day, slot, sem, timetable, teacher_bookings, room_bookings, teachers, classrooms, subjects_per_sem)

    df = pd.DataFrame([
        {"Day": day, **{slots[s]: timetable[day][s] for s in slots.keys()}}
        for day in days
    ])
    return df
