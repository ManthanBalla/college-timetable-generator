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

    # Teacher clash
    teacher_clash = all_tt[
        (all_tt["Day"] == day) &
        (all_tt["Time Slot"] == time_slot) &
        (all_tt["Teacher"] == teacher) &
        (all_tt["Semester_File"] != f"timetable_{current_sem}.csv")
    ]
    if not teacher_clash.empty:
        clash_info = teacher_clash.iloc[0]
        return f"❌ {teacher} is already teaching {clash_info['Subject']} in {clash_info['Room/Lab']} on {day} {time_slot}."

    # Room/Lab clash
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

    # Filter subjects
    if sem_num in [1, 2]:  # First year: ALL branches same
        subjects = subjects_df[subjects_df["Semester"] == sem_num]["Subject"].tolist()
    else:
        subjects = subjects_df[
            (subjects_df["Semester"] == sem_num) &
            ((subjects_df["Branch"] == branch) | (subjects_df["Branch"] == "ALL"))
        ]["Subject"].tolist()

    teachers = teachers_df["Teacher_Name"].tolist()
    rooms = classrooms_df["Room_Name"].tolist()

    timetable = []

    # Pick 4 lab days
    lab_days = random.sample(days, min(4, len(days)))

    # Pick unique lab subjects (up to 4, or fewer if not enough)
    lab_subjects = random.sample(subjects, min(4, len(subjects)))
    lab_assignment = dict(zip(lab_days, lab_subjects))

    for day in days:
        used_teachers = set()
        used_rooms = set()
        subjects_used_today = set()

        for slot in slots:
            # Handle fixed breaks
            if "Tea Break" in slot:
                timetable.append({
                    "Day": day,
                    "Time Slot": slot,
                    "Subject": "Tea Break",
                    "Teacher": "-",
                    "Room/Lab": "-"
                })
                continue

            if "Lunch Break" in slot:
                timetable.append({
                    "Day": day,
                    "Time Slot": slot,
                    "Subject": "Lunch Break",
                    "Teacher": "-",
                    "Room/Lab": "-"
                })
                continue

            # Lab allocation (only once per week per subject)
            if day in lab_assignment and slot == "11:30-12:30":
                lab_subject = lab_assignment[day]
                lab_teacher = random.choice(teachers)
                lab_room = random.choice(rooms)

                timetable.append({
                    "Day": day,
                    "Time Slot": "11:30-12:30",
                    "Subject": f"{lab_subject} (Lab)",
                    "Teacher": lab_teacher,
                    "Room/Lab": lab_room
                })
                timetable.append({
                    "Day": day,
                    "Time Slot": "12:30-1:30",
                    "Subject": f"{lab_subject} (Lab)",
                    "Teacher": lab_teacher,
                    "Room/Lab": lab_room
                })

                subjects_used_today.add(lab_subject)
                continue  # skip 12:30 since already added above

            if day in lab_assignment and slot == "12:30-1:30":
                continue  # already handled with the lab

            # Normal lecture slots
            available_subjects = [s for s in subjects if s not in subjects_used_today]
            if not available_subjects:
                continue

            subject = random.choice(available_subjects)
            teacher = random.choice([t for t in teachers if t not in used_teachers]) if teachers else "TBD"
            room = random.choice([r for r in rooms if r not in used_rooms]) if rooms else "TBD"

            timetable.append({
                "Day": day,
                "Time Slot": slot,
                "Subject": subject,
                "Teacher": teacher,
                "Room/Lab": room
            })

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
# Dashboard
# ---------------------------
if menu == "Dashboard":
    st.title("📊 Dashboard - College Timetable")

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
# Manual Timetable Section
# ---------------------------
elif menu == "Create Timetable":
    st.title("🛠 Create Timetable Manually")

    year = st.selectbox("Select Year", list(year_semesters.keys()))
    semester = st.selectbox("Select Semester", year_semesters[year])
    file_name = f"timetable_{semester}.csv"

    teachers_df = load_teachers()
    classrooms_df = load_classrooms()
    subjects_df = load_subjects()

    if teachers_df.empty or classrooms_df.empty or subjects_df.empty:
        st.error("⚠ Please make sure teachers.csv, classrooms.csv, and subjects.csv are present.")
    else:
        if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
            timetable_df = pd.read_csv(file_name)
        else:
            timetable_df = pd.DataFrame(columns=["Day", "Time Slot", "Subject", "Teacher", "Room/Lab"])

        # Delete Entry
        if "delete_index" in st.session_state:
            timetable_df = timetable_df.drop(st.session_state.delete_index).reset_index(drop=True)
            timetable_df.to_csv(file_name, index=False)
            st.success("✅ Entry deleted successfully.")
            del st.session_state.delete_index

        # Edit Entry
        if "edit_index" in st.session_state:
            edit_row = timetable_df.loc[st.session_state.edit_index]
            st.subheader(f"✏ Editing Entry {st.session_state.edit_index + 1}")

            day = st.selectbox("Select Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                               index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(edit_row["Day"]))
            time_slot = st.selectbox("Select Time Slot", [
                "9:15-10:15", "10:15-11:15", "11:30-12:30",
                "12:30-1:30", "2:00-3:00", "3:00-4:00"
            ], index=[
                "9:15-10:15", "10:15-11:15", "11:30-12:30",
                "12:30-1:30", "2:00-3:00", "3:00-4:00"
            ].index(edit_row["Time Slot"]))

            sem_num = int(semester.split()[-1])
            subj_list = subjects_df[subjects_df["Semester"] == sem_num]["Subject"].tolist()
            subject = st.selectbox("Select Subject", subj_list, index=subj_list.index(edit_row["Subject"]))
            teacher = st.selectbox("Select Teacher", teachers_df["Teacher_Name"].tolist(),
                                   index=teachers_df["Teacher_Name"].tolist().index(edit_row["Teacher"]))
            room_lab = st.selectbox("Select Room/Lab", classrooms_df["Room_Name"].tolist(),
                                    index=classrooms_df["Room_Name"].tolist().index(edit_row["Room/Lab"]))

            if st.button("Save Changes"):
                clash_msg = check_clash(day, time_slot, teacher, room_lab, semester)
                if clash_msg:
                    st.error(clash_msg)
                else:
                    timetable_df.at[st.session_state.edit_index, "Day"] = day
                    timetable_df.at[st.session_state.edit_index, "Time Slot"] = time_slot
                    timetable_df.at[st.session_state.edit_index, "Subject"] = subject
                    timetable_df.at[st.session_state.edit_index, "Teacher"] = teacher
                    timetable_df.at[st.session_state.edit_index, "Room/Lab"] = room_lab
                    timetable_df.to_csv(file_name, index=False)
                    st.success("✅ Entry updated successfully.")
                    del st.session_state.edit_index

        # Show timetable with edit/delete buttons
        st.subheader(f"📅 Current Timetable for {semester}")
        for idx, row in timetable_df.iterrows():
            st.write(f"{row['Day']} | {row['Time Slot']} | {row['Subject']} | {row['Teacher']} | {row['Room/Lab']}")
            col1, col2 = st.columns([0.1, 0.1])
            if col1.button("✏ Edit", key=f"edit_{idx}"):
                st.session_state.edit_index = idx
            if col2.button("🗑 Delete", key=f"delete_{idx}"):
                st.session_state.delete_index = idx

        # Add new entry
        st.subheader("➕ Add New Entry")
        day = st.selectbox("Select Day (New Entry)", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        time_slot = st.selectbox("Select Time Slot (New Entry)", [
            "9:15-10:15", "10:15-11:15", "11:30-12:30",
            "12:30-1:30", "2:00-3:00", "3:00-4:00"
        ])
        sem_num = int(semester.split()[-1])
        subj_list = subjects_df[subjects_df["Semester"] == sem_num]["Subject"].tolist()
        subject = st.selectbox("Select Subject (New Entry)", subj_list)
        teacher = st.selectbox("Select Teacher (New Entry)", teachers_df["Teacher_Name"].tolist())
        room_lab = st.selectbox("Select Room/Lab (New Entry)", classrooms_df["Room_Name"].tolist())

        if st.button("Add Entry"):
            clash_msg = check_clash(day, time_slot, teacher, room_lab, semester)
            if clash_msg:
                st.error(clash_msg)
            else:
                new_entry = pd.DataFrame([{
                    "Day": day,
                    "Time Slot": time_slot,
                    "Subject": subject,
                    "Teacher": teacher,
                    "Room/Lab": room_lab
                }])
                timetable_df = pd.concat([timetable_df, new_entry], ignore_index=True)
                timetable_df.to_csv(file_name, index=False)
                st.success(f"✅ Entry added to {semester} timetable.")

# ---------------------------
# View Teachers Data
# ---------------------------
elif menu == "View Teachers Data":
    st.title("👨‍🏫 Teachers Data")
    df = load_teachers()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.error("teachers.csv not found.")

# ---------------------------
# View Lab Data
# ---------------------------
elif menu == "View Lab Data":
    st.title("🏫 Lab/Classroom Data")
    df = load_classrooms()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.error("classrooms.csv not found.")

# ---------------------------
# View Subjects Data
# ---------------------------
elif menu == "View Subjects Data":
    st.title("📘 Subjects Data")
    df = load_subjects()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.error("subjects.csv not found.")

# ---------------------------
# Check Conflicts
# ---------------------------
elif menu == "Check Conflicts":
    st.title("⚠ Check Conflicts")
    all_tt = load_all_timetables()
    if all_tt.empty:
        st.info("No timetables found.")
    else:
        st.dataframe(all_tt, use_container_width=True)

# ---------------------------
# AI Timetable Generator
# ---------------------------
elif menu == "AI Timetable Generator":
    st.title("🤖 AI Timetable Generator")

    branch = st.selectbox("Select Branch", branches)
    year = st.selectbox("Select Year", list(year_semesters.keys()))
    semester = st.selectbox("Select Semester", year_semesters[year])

    teachers_df = load_teachers()
    classrooms_df = load_classrooms()
    subjects_df = load_subjects()

    if st.button("Generate Timetable Automatically"):
        if teachers_df.empty or classrooms_df.empty or subjects_df.empty:
            st.error("⚠ Please make sure teachers.csv, classrooms.csv, and subjects.csv are present.")
        else:
            file_name = f"timetable_{branch}_{semester}.csv"
            timetable = generate_ai_timetable(branch, semester, teachers_df, classrooms_df, subjects_df)
            timetable.to_csv(file_name, index=False)
            st.success(f"✅ AI-generated timetable saved as {file_name}")
            st.dataframe(timetable, use_container_width=True)

# ---------------------------
# AI Generated Timetables Viewer
# ---------------------------
elif menu == "AI Generated Timetables":
    st.title("📂 All AI Generated Timetables")

    all_tt = load_all_timetables()
    if all_tt.empty:
        st.info("No AI-generated timetables found yet.")
    else:
        file_list = sorted(set(all_tt["Semester_File"].tolist()))
        selected_file = st.selectbox("Select Timetable File", file_list)

        df = pd.read_csv(selected_file)
        st.success(f"Showing timetable: {selected_file}")
        st.dataframe(df, use_container_width=True)
