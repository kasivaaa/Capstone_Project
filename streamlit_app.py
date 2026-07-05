import streamlit as st
import sqlite3
import hashlib
import os
import shutil
from datetime import datetime

# -------------------------------
# DATABASE
# -------------------------------

DB_NAME = "education_management.db"

#-------------------------------
# CONNECTION TO DATABASE
#-------------------------------
def get_connection():
    return sqlite3.connect(DB_NAME)

#-------------------------------
# PASSWORD HASHING
#-------------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#-------------------------------
# USER AUTHENTICATION
#-------------------------------

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, username FROM Users
        WHERE username = ? AND password = ?
    """, (username, hash_password(password)))

    user = cursor.fetchone()
    conn.close()
    return user

#-------------------------------
#FETCH DATA 
#------------------------------
def fetch_data(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data
#-------------------------------
# EXECUTE QUERY
#------------------------------

def execute_query(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

#-------------------------------
# EXECUTE QUERY WITH FEEDBACK
#-------------------------------

def execute_query_with_feedback(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected

def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

# -------------------------------
# STREAMLIT SETUP
# -------------------------------

st.set_page_config(
    page_title="Education Management System",
    page_icon="📚",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# -------------------------------
# LOGIN PAGE
# -------------------------------

if not st.session_state.logged_in:
    st.title("📚 Education Management System")
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(username, password)

        if user:
            role, logged_username = user
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.username = logged_username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# -------------------------------
# MAIN APP
# -------------------------------

else:
    st.sidebar.title("📚 EMS Menu")
    st.sidebar.write(f"User: **{st.session_state.username}**")
    st.sidebar.write(f"Role: **{st.session_state.role}**")

    role = st.session_state.role

    menu_options = ["Dashboard", "Students", "Teachers", "Courses", "Grades", "Attendance", "Reports", "Settings"]

    menu = st.sidebar.radio("Navigation", menu_options)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

    st.title("📚 Education Management System")

    # -------------------------------
    # DASHBOARD
    # -------------------------------
    if menu == "Dashboard":
        st.subheader("System Dashboard")

        total_students = fetch_data("SELECT COUNT(*) FROM Students")[0][0]
        total_teachers = fetch_data("SELECT COUNT(*) FROM Teachers")[0][0]
        total_courses = fetch_data("SELECT COUNT(*) FROM Courses")[0][0]
        total_grades = fetch_data("SELECT COUNT(*) FROM Grades")[0][0]
        total_attendance = fetch_data("SELECT COUNT(*) FROM Attendance")[0][0]

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Students", total_students)
        col2.metric("Teachers", total_teachers)
        col3.metric("Courses", total_courses)
        col4.metric("Grades", total_grades)
        col5.metric("Attendance", total_attendance)

    # -------------------------------
    # STUDENTS
    # -------------------------------
    elif menu == "Students":
        st.subheader("Student Management")

    if role == "admin":
        with st.expander("Add Student"):
            name = st.text_input("Student Name")
            course = st.text_input("Course")
            age = st.number_input("Age", min_value=1, step=1)
            email = st.text_input("Email")
            username = st.text_input("Student Username")
            password = st.text_input("Student Password", type="password")

            if st.button("Add Student"):
                execute_query_with_feedback("""
                    INSERT OR IGNORE INTO Students(name, course, age, email, username)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, course, age, email, username))

                execute_query_with_feedback("""
                    INSERT OR IGNORE INTO Users(username, password, role)
                    VALUES (?, ?, ?)
                """, (username, hash_password(password), "student"))

                st.success("Student and login account added successfully!")

    search_name = st.text_input("Search student by name")

    if search_name:
        students = fetch_data(
            "SELECT * FROM Students WHERE name LIKE ?",
            (f"%{search_name}%",)
        )
    else:
        students = fetch_data("SELECT * FROM Students")

    st.dataframe(students, use_container_width=True)

    if role == "admin":
        with st.expander("Update Student"):
            student_id = st.number_input("Student ID to update", min_value=1, step=1, key="update_student_id")
            new_name = st.text_input("New Name")
            new_course = st.text_input("New Course")
            new_age = st.number_input("New Age", min_value=1, step=1)
            new_email = st.text_input("New Email")

            if st.button("Update Student"):
                rows = execute_query_with_feedback("""
                    UPDATE Students
                    SET name = ?, course = ?, age = ?, email = ?
                    WHERE student_id = ?
                """, (new_name, new_course, new_age, new_email, student_id))

                if rows > 0:
                    st.success("Student updated successfully!")
                else:
                    st.error("Student ID not found.")

        with st.expander("Delete Student"):
            student_id = st.number_input("Student ID to delete", min_value=1, step=1, key="delete_student_id")

            if st.button("Delete Student"):
                rows = execute_query_with_feedback(
                    "DELETE FROM Students WHERE student_id = ?",
                    (student_id,)
                )

                if rows > 0:
                    st.warning("Student deleted successfully.")
                else:
                    st.error("Student ID not found.")

    # -------------------------------
    # TEACHERS
    # -------------------------------
    elif menu == "Teachers":
        st.subheader("Teacher Management")

    if role in ["admin", "teacher"]:
        with st.expander("Add Teacher"):
            name = st.text_input("Teacher Name")
            subject = st.text_input("Subject")
            email = st.text_input("Teacher Email")

            if st.button("Add Teacher"):
                rows = execute_query_with_feedback("""
                    INSERT OR IGNORE INTO Teachers(name, subject, email)
                    VALUES (?, ?, ?)
                """, (name, subject, email))

                if rows > 0:
                    st.success("Teacher added successfully!")
                else:
                    st.warning("Teacher already exists.")

    search_teacher = st.text_input("Search teacher by name")

    if search_teacher:
        teachers = fetch_data(
            "SELECT * FROM Teachers WHERE name LIKE ?",
            (f"%{search_teacher}%",)
        )
    else:
        teachers = fetch_data("SELECT * FROM Teachers")

    st.dataframe(teachers, use_container_width=True)

    if role == "admin":
        with st.expander("Update Teacher"):
            teacher_id = st.number_input("Teacher ID to update", min_value=1, step=1, key="update_teacher_id")
            new_name = st.text_input("New Teacher Name")
            new_subject = st.text_input("New Subject")
            new_email = st.text_input("New Teacher Email")

            if st.button("Update Teacher"):
                rows = execute_query_with_feedback("""
                    UPDATE Teachers
                    SET name = ?, subject = ?, email = ?
                    WHERE teacher_id = ?
                """, (new_name, new_subject, new_email, teacher_id))

                if rows > 0:
                    st.success("Teacher updated successfully!")
                else:
                    st.error("Teacher ID not found.")

     
        with st.expander("Add Teacher Account"):
            t_name = st.text_input("Teacher Name (for account)", key="acct_name")
            t_subject = st.text_input("Subject (for account)", key="acct_subject")
            t_email = st.text_input("Teacher Email (for account)", key="acct_email")
            teacher_username = st.text_input("Teacher Username", key="acct_username")
            teacher_password = st.text_input("Teacher Password", type="password", key="acct_password")

            if st.button("Add Teacher with Account"):
                teacher_rows = execute_query_with_feedback("""
                    INSERT OR IGNORE INTO Teachers(name, subject, email)
                    VALUES (?, ?, ?)
                """, (t_name, t_subject, t_email))

                user_rows = execute_query_with_feedback("""
                    INSERT OR IGNORE INTO Users(username, password, role)
                    VALUES (?, ?, ?)
                """, (teacher_username, hash_password(teacher_password), "teacher"))

                if teacher_rows > 0 or user_rows > 0:
                    st.success("Teacher and login account added successfully!")
                else:
                    st.warning("Teacher or username already exists.")
    # -------------------------------
    # COURSES
    # -------------------------------
    elif menu == "Courses":
        st.subheader("Course Management")

        if role == "admin":
            with st.expander("Add Course"):
                course_name = st.text_input("Course Name")
                teacher_id = st.number_input("Teacher ID", min_value=1, step=1)

                if st.button("Add Course"):
                    execute_query("""
                        INSERT OR IGNORE INTO Courses(course_name, teacher_id)
                        VALUES (?, ?)
                    """, (course_name, teacher_id))
                    st.success("Course added successfully!")

        courses = fetch_data("""
            SELECT Courses.course_id, Courses.course_name, Teachers.name
            FROM Courses
            LEFT JOIN Teachers ON Courses.teacher_id = Teachers.teacher_id
        """)
        st.dataframe(courses, use_container_width=True)

    # -------------------------------
    # GRADES
    # -------------------------------
    elif menu == "Grades":
        st.subheader("Grade Management")

        if role in ["admin", "teacher"]:
            with st.expander("Add Grade"):
                student_id = st.number_input("Student ID", min_value=1, step=1)
                course_id = st.number_input("Course ID", min_value=1, step=1)
                score = st.number_input("Score", min_value=0, max_value=100, step=1)

                if st.button("Add Grade"):
                    execute_query("""
                        INSERT INTO Grades(student_id, course_id, score)
                        VALUES (?, ?, ?)
                    """, (student_id, course_id, score))
                    st.success("Grade added successfully!")

        grades = fetch_data("""
            SELECT Students.name, Courses.course_name, Grades.score
            FROM Grades
            JOIN Students ON Grades.student_id = Students.student_id
            JOIN Courses ON Grades.course_id = Courses.course_id
        """)
        st.dataframe(grades, use_container_width=True)

    # -------------------------------
    # ATTENDANCE
    # -------------------------------
    elif menu == "Attendance":
        st.subheader("Attendance Management")

        if role in ["admin", "teacher"]:
            with st.expander("Mark Attendance"):
                student_id = st.number_input("Student ID", min_value=1, step=1)
                course_id = st.number_input("Course ID", min_value=1, step=1)
                date = st.date_input("Attendance Date")
                status = st.selectbox("Status", ["Present", "Absent"])

                if st.button("Mark Attendance"):
                    execute_query("""
                        INSERT INTO Attendance(student_id, course_id, attendance_date, status)
                        VALUES (?, ?, ?, ?)
                    """, (student_id, course_id, str(date), status))
                    st.success("Attendance marked successfully!")

        attendance = fetch_data("""
            SELECT Students.name, Courses.course_name, Attendance.attendance_date, Attendance.status
            FROM Attendance
            JOIN Students ON Attendance.student_id = Students.student_id
            JOIN Courses ON Attendance.course_id = Courses.course_id
        """)
        st.dataframe(attendance, use_container_width=True)

    # -------------------------------
    # REPORTS
    # -------------------------------
    elif menu == "Reports":
        st.subheader("Generated Reports")

        create_folder("Reports")

        reports = os.listdir("Reports")

        if reports:
            for report in reports:
                file_path = os.path.join("Reports", report)

                with open(file_path, "rb") as file:
                    st.download_button(
                        label=f"Download {report}",
                        data=file,
                        file_name=report
                    )
        else:
            st.info("No reports generated yet.")

    # -------------------------------
    # SETTINGS
    # -------------------------------
    elif menu == "Settings":
        st.subheader("Settings")

        st.write("Change Password")

        old_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")

        if st.button("Change Password"):
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                user = login_user(st.session_state.username, old_password)

                if user:
                    execute_query("""
                        UPDATE Users
                        SET password = ?
                        WHERE username = ?
                    """, (hash_password(new_password), st.session_state.username))

                    st.success("Password changed successfully!")
                else:
                    st.error("Current password is incorrect.")

        if role == "admin":
            st.divider()
            st.write("Database Backup")

            if st.button("Backup Database"):
                create_folder("Backups")
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                backup_file = f"Backups/education_management_backup_{timestamp}.db"
                shutil.copy(DB_NAME, backup_file)
                st.success(f"Database backed up successfully: {backup_file}")