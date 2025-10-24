import streamlit as st
import pandas as pd
import os
import random

# ---------------------------
# Load CSV Data
# ---------------------------
def load_teachers():
    return pd.read_csv("teachers.csv") if os.path.exists("teachers.csv") else pd.DataFrame()

def load_classrooms():
    return pd.read_csv("classrooms.csv") if os.path.exists("classrooms.csv") else pd.DataFrame()

def load_subjects():
    return pd.read_csv("subjects.csv") if os.path.exists("subjects.csv") else pd.DataFrame()

REQUIRED_COLUMNS = {"Day", "Time Slot", "Subject", "Teacher", "Room/Lab"}

def load_all_timetables():
    timetables = []
    for file in os.listdir():
        if file.startswith("timetable_") and file.endswith(".csv"):
            try:
                if os.path.getsize(file) > 0:
                    df = pd.read_csv(file)
                    if not df.empty and REQUIRED_COLUMNS.issubset(df.columns):
                        df["Semester_File"] = file
                        timetables.append(df)
                    else:
                        st.warning(f"Skipping {file} — missing required columns.")
            except Exception as e:
                st.warning(f"Skipping file {file} due to read error: {e}")
    return pd.concat(timetables, ignore_index=True) if timetables else pd.DataFrame()

# ---------------------------
# Clash Detection
# ---------------------------
def check_clash(day, time_slot, teacher, room_lab, current_sem):
    all_tt = load_all_timetables()
    if all_tt.empty:
        return None

    teacher_clash = all_tt[
        (all_tt["Day"] == day) &
        (all_tt["Time Slot"] == time_slot) &
        (all_tt["Teacher"] == teacher) &
        (all_tt["Semester_File"] != f"timetable_{current_sem}.csv")
    ]
    if not teacher_clash.empty:
        clash_info = teacher_clash.iloc[0]
        return f"❌ {teacher} is already teaching {clash_info['Subject']} in {clash_info['Room/Lab']} on {day} {time_slot}."

    room_clash = all_tt[
        (all_tt["Day"] == day) &
        (all_tt["Time Slot"] == time_slot) &
        (all_tt["Room/Lab"] == room_lab) &
        (all_tt["Semester_File"] != f"timetable_{current_sem}.csv")
    ]
    if not room_clash.empty:
        clash_info = room_clash.iloc[0]
        return f"❌ {room_lab} is already booked for {clash_info['Subject']} by {clash_info['Teacher']} on {day} {time_slot}."

    return None

# ---------------------------
# Year-Sem Mapping
# ---------------------------
year_semesters = {
    "First Year": ["Semester 1", "Semester 2"],
    "Second Year": ["Semester 3", "Semester 4"],
    "Third Year": ["Semester 5", "Semester 6"],
    "Final Year": ["Semester 7", "Semester 8"]
}

# ---------------------------
# Branches
# ---------------------------
branches = ["AIDS", "COMPS", "CSD", "IT", "Mechanical", "Civil", "Mechatronics"]

# ---------------------------
# AI Timetable Generator Logic
# ---------------------------
def generate_ai_timetable(branch, semester, teachers_df, classrooms_df, subjects_df):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots = [
        "9:15-10:15",
        "10:15-11:15",
        "Tea Break (11:15-11:30)",
        "11:30-12:30",
        "12:30-1:30",
        "Lunch Break (1:30-2:00)",
        "2:00-3:00",
        "3:00-4:00"
    ]

    sem_num = int(semester.split()[-1])

    if sem_num in [1, 2]:
        subjects = subjects_df[subjects_df["Semester"] == sem_num]["Subject"].tolist()
    else:
        subjects = subjects_df[
            (subjects_df["Semester"] == sem_num) &
            ((subjects_df["Branch"] == branch) | (subjects_df["Branch"] == "ALL"))
        ]["Subject"].tolist()

    teachers = teachers_df["Teacher_Name"].tolist()
    rooms = classrooms_df["Room_Name"].tolist()
    timetable = []

    lab_days = random.sample(days, min(4, len(days)))
    lab_subjects = random.sample(subjects, min(4, len(subjects)))
    lab_assignment = dict(zip(lab_days, lab_subjects))

    for day in days:
        used_teachers = set()
        used_rooms = set()
        subjects_used_today = set()

        for slot in slots:
            if "Tea Break" in slot:
                timetable.append({"Day": day, "Time Slot": slot, "Subject": "Tea Break", "Teacher": "-", "Room/Lab": "-"})
                continue

            if "Lunch Break" in slot:
                timetable.append({"Day": day, "Time Slot": slot, "Subject": "Lunch Break", "Teacher": "-", "Room/Lab": "-"})
                continue

            if day in lab_assignment and slot == "11:30-12:30":
                lab_subject = lab_assignment[day]
                lab_teacher = random.choice(teachers)
                lab_room = random.choice(rooms)
                timetable.append({"Day": day, "Time Slot": "11:30-12:30", "Subject": f"{lab_subject} (Lab)", "Teacher": lab_teacher, "Room/Lab": lab_room})
                timetable.append({"Day": day, "Time Slot": "12:30-1:30", "Subject": f"{lab_subject} (Lab)", "Teacher": lab_teacher, "Room/Lab": lab_room})
                subjects_used_today.add(lab_subject)
                continue

            if day in lab_assignment and slot == "12:30-1:30":
                continue

            available_subjects = [s for s in subjects if s not in subjects_used_today]
            if not available_subjects:
                continue

            subject = random.choice(available_subjects)
            teacher = random.choice([t for t in teachers if t not in used_teachers]) if teachers else "TBD"
            room = random.choice([r for r in rooms if r not in used_rooms]) if rooms else "TBD"

            timetable.append({"Day": day, "Time Slot": slot, "Subject": subject, "Teacher": teacher, "Room/Lab": room})
            used_teachers.add(teacher)
            used_rooms.add(room)
            subjects_used_today.add(subject)

    return pd.DataFrame(timetable)

# ---------------------------
# Sidebar Menu
# ---------------------------
menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Create Timetable",
        "View Teachers Data",
        "View Lab Data",
        "View Subjects Data",
        "Check Conflicts",
        "AI Timetable Generator",
        "AI Generated Timetables"
    ]
)

# ---------------------------
# Dashboard (with Google AdSense)
# ---------------------------
if menu == "Dashboard":
    st.title("📊 Dashboard - College Timetable")

    # ✅ Google AdSense Integration
    st.markdown("""
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3249724202170570" crossorigin="anonymous"></script> <!-- Streamlit Dashboard Ad --> <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-3249724202170570" data-ad-slot="5516555758" data-ad-format="auto" data-full-width-responsive="true"></ins> <script> (adsbygoogle = window.adsbygoogle || []).push({}); </script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3249724202170570"
     crossorigin="anonymous"></script>
    """, unsafe_allow_html=True)

    year = st.selectbox("Select Year", list(year_semesters.keys()))
    semester = st.selectbox("Select Semester", year_semesters[year])

    file_name = f"timetable_{semester}.csv"
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        st.success(f"Showing timetable for {semester}")
        df = pd.read_csv(file_name)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning(f"No timetable found for {semester}. Please go to 'Create Timetable' and generate one.")

# ---------------------------
# The rest of your code (unchanged)
# ---------------------------
