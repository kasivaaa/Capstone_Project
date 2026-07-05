# ----------------------------------------------
# Education Management System
# ----------------------------------------------

import sqlite3
import hashlib
import os
import shutil
from datetime import datetime

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
conn = sqlite3.connect("education_management.db")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# -------------------------------
# PASSWORD HASHING
# -------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_reports_folder():
    if not os.path.exists("Reports"):
        os.makedirs("Reports")


def create_backups_folder():
    if not os.path.exists("Backups"):
        os.makedirs("Backups")

# -------------------------------
# TABLES
# -------------------------------

#------------------------------
# STUDENT TABLE
#------------------------------


cursor.execute("""
CREATE TABLE IF NOT EXISTS Students(
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    name TEXT NOT NULL,
    course_id INTEGER,
    age INTEGER,
    email TEXT UNIQUE,
    FOREIGN KEY(user_id) REFERENCES Users(user_id),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
)
""") 

try:
    cursor.execute("ALTER TABLE Students ADD COLUMN username TEXT")
    conn.commit()
except sqlite3.OperationalError:
    # The column already exists
    pass

#-------------------------------
# TEACHER TABLE
#------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS Teachers(
    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    email TEXT UNIQUE,
    FOREIGN KEY(user_id) REFERENCES Users(user_id)
)
""")
#-------------------------------
# COURSE TABLE
#-------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS Courses(
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT UNIQUE NOT NULL,
    teacher_id INTEGER,
    FOREIGN KEY(teacher_id) REFERENCES Teachers(teacher_id)
)
""")
#-------------------------------
# GRADES TABLE
#-------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS Grades(
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    FOREIGN KEY(student_id) REFERENCES Students(student_id),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
)
""")

conn.commit()
#-------------------------------
# ATTENDANCE TABLE
#-------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS Attendance(
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES Students(student_id),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
)
""")

conn.commit()


#-------------------------------
# USER TABLE
#-------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

conn.commit()

# -------------------------------
# SAMPLE USERS
# -------------------------------
# -------------------------------
# SAMPLE USERS
# -------------------------------

cursor.execute("DELETE FROM Users")

cursor.executemany("""
INSERT INTO Users(username, password, role)
VALUES (?, ?, ?)
""", [
    ("admin", hash_password("admin123"), "admin"),
    ("teacher1", hash_password("teach123"), "teacher"),

    # Student login accounts
    ("nicole1", hash_password("stud123"), "student"),
    ("john1", hash_password("stud123"), "student")
])

conn.commit()

# -------------------------------
# SAMPLE STUDENTS
# -------------------------------
students = [
    ("Nicole Kasiva", "Computer Science", 22, "nicole@tebuschool.com", "nicole1"),
    ("John Mwangi", "Information Technology", 28, "john@tebuschool.com", "john1")
]

cursor.executemany("""
INSERT OR IGNORE INTO Students(name, course, age, email, username)
VALUES (?, ?, ?, ?, ?)
""", students)

conn.commit()


cursor.execute("""
UPDATE Students
SET username = 'nicole1'
WHERE email = 'nicole@tebuschool.com'
""")

cursor.execute("""
UPDATE Students
SET username = 'john1'
WHERE email = 'john@tebuschool.com'
""")

conn.commit()

# -------------------------------
# STUDENT FUNCTIONS
# -------------------------------

#-------------------------------
# ADD STUDENTS
#-------------------------------


def add_student():
    try:
        name = input("Name: ")
        course = input("Course: ")
        age = int(input("Age: "))
        email = input("Email: ")

        cursor.execute("""
            INSERT OR IGNORE INTO Students(name, course, age, email)
            VALUES (?, ?, ?, ?)
        """, (name, course, age, email))

        conn.commit()

        if cursor.rowcount > 0:
            print("Student added successfully!\n")
        else:
            print("Student already exists.\n")

    except ValueError:
        print("Invalid age. Please enter a number.\n")

#-------------------------------
# VIEW STUDENTS
#-------------------------------

def view_students():
    cursor.execute("SELECT * FROM Students")
    students = cursor.fetchall()

    print("\nALL STUDENTS")
    print("-" * 40)

    if students:
        for student in students:
            print(student)
    else:
        print("No students found.")

#-------------------------------
# SEARCH STUDENTS
#-------------------------------

def search_student():
    name = input("Enter student name: ")

    cursor.execute("SELECT * FROM Students WHERE name = ?", (name,))
    student = cursor.fetchone()

    if student:
        print("\nStudent Found:")
        print(student)
    else:
    
        print("Student not found.")


#-------------------------------
# UPDATE STUDENTS
#-------------------------------

def update_student():
    try:
        student_id = int(input("Enter Student ID to update: "))
    except ValueError:
        print("Invalid Student ID.\n")
        return

    cursor.execute("SELECT * FROM Students WHERE student_id = ?", (student_id,))
    data = cursor.fetchone()

    if not data:
        print("Student not found.\n")
        return

    try:
        name = input(f"Name [{data[1]}]: ") or data[1]
        course = input(f"Course [{data[2]}]: ") or data[2]

        age_input = input(f"Age [{data[3]}]: ")
        age = int(age_input) if age_input else data[3]

        email = input(f"Email [{data[4]}]: ") or data[4]

        cursor.execute("""
            UPDATE Students
            SET name = ?, course = ?, age = ?, email = ?
            WHERE student_id = ?
        """, (name, course, age, email, student_id))

        conn.commit()
        print("Student updated successfully!\n")

    except ValueError:
        print("Invalid age. Please enter a number.\n")

#-------------------------------
# DELETE STUDENTS
#-------------------------------

def delete_student():
    try:
        student_id = int(input("Enter Student ID to delete: "))
    except ValueError:
        print("Invalid Student ID.\n")
        return

    cursor.execute("DELETE FROM Students WHERE student_id = ?", (student_id,))
    conn.commit()

    if cursor.rowcount > 0:
        print("Student deleted successfully!\n")
    else:
        print("Student not found.\n")

#-------------------------------
# VIEW MY DETAILS
#-------------------------------


def view_my_details(username):
    cursor.execute("""
        SELECT student_id, name, course, age, email
        FROM Students
        WHERE username = ?
    """, (username,))

    student = cursor.fetchone()

    if student:
        print("\nMY PROFILE")
        print("-" * 40)
        print(f"Student ID : {student[0]}")
        print(f"Name       : {student[1]}")
        print(f"Course     : {student[2]}")
        print(f"Age        : {student[3]}")
        print(f"Email      : {student[4]}")
    else:
        print("No student profile linked to this account.")

# -------------------------------
# TEACHER FUNCTIONS
# -------------------------------


#------------------------------
# ADD TEACHERS
#------------------------------

def add_teacher():
    name = input("Teacher name: ")
    subject = input("Subject: ")
    email = input("Email: ")

    cursor.execute("""
        INSERT OR IGNORE INTO Teachers(name, subject, email)
        VALUES (?, ?, ?)
    """, (name, subject, email))

    conn.commit()

    if cursor.rowcount > 0:
        print("Teacher added successfully!\n")
    else:
        print("Teacher already exists.\n")

#-------------------------------
# VIEW TEACHERS
#-------------------------------

def view_teachers():
    cursor.execute("SELECT * FROM Teachers")
    teachers = cursor.fetchall()

    print("\nALL TEACHERS")
    print("-" * 40)

    if teachers:
        for teacher in teachers:
            print(teacher)
    else:
        print("No teachers found.")

#-------------------------------
# SEARCH TEACHERS
#-------------------------------

def search_teacher():
    name = input("Enter teacher name: ")

    cursor.execute("SELECT * FROM Teachers WHERE name = ?", (name,))
    teacher = cursor.fetchone()

    if teacher:
        print("\nTeacher Found:")
        print(teacher)
    else:
        print("Teacher not found.")
#-------------------------------
# UPDATE TEACHERS
#-------------------------------

def update_teacher():
    try:
        teacher_id = int(input("Enter Teacher ID to update: "))
    except ValueError:
        print("Invalid Teacher ID.\n")
        return

    cursor.execute("SELECT * FROM Teachers WHERE teacher_id = ?", (teacher_id,))
    data = cursor.fetchone()

    if not data:
        print("Teacher not found.\n")
        return

    name = input(f"Name [{data[1]}]: ") or data[1]
    subject = input(f"Subject [{data[2]}]: ") or data[2]
    email = input(f"Email [{data[3]}]: ") or data[3]

    cursor.execute("""
        UPDATE Teachers
        SET name = ?, subject = ?, email = ?
        WHERE teacher_id = ?
    """, (name, subject, email, teacher_id))

    conn.commit()
    print("Teacher updated successfully!\n")


#-------------------------------
# DELETE TEACHERS
#-------------------------------

def delete_teacher():
    try:
        teacher_id = int(input("Enter Teacher ID to delete: "))
    except ValueError:
        print("Invalid Teacher ID.\n")
        return

    cursor.execute("DELETE FROM Teachers WHERE teacher_id = ?", (teacher_id,))
    conn.commit()

    if cursor.rowcount > 0:
        print("Teacher deleted successfully!\n")
    else:
        print("Teacher not found.\n")


def handle_add_teacher(role):
    if role in ["admin", "teacher"]:
        add_teacher()
    else:
        print("Access denied.\n")


# -------------------------------
# COURSE FUNCTIONS
# -------------------------------
def add_course():
    course_name = input("Course name: ")

    try:
        teacher_id = int(input("Teacher ID assigned to this course: "))
    except ValueError:
        print("Invalid Teacher ID.\n")
        return

    cursor.execute("SELECT * FROM Teachers WHERE teacher_id = ?", (teacher_id,))
    teacher = cursor.fetchone()

    if not teacher:
        print("Teacher ID does not exist. Add the teacher first.\n")
        return

    cursor.execute("""
        INSERT OR IGNORE INTO Courses(course_name, teacher_id)
        VALUES (?, ?)
    """, (course_name, teacher_id))

    conn.commit()

    if cursor.rowcount > 0:
        print("Course added successfully!\n")
    else:
        print("Course already exists.\n")

#-------------------------------
# VIEW COURSES
#-------------------------------

def view_courses():
    cursor.execute("""
        SELECT Courses.course_id, Courses.course_name, Teachers.name
        FROM Courses
        LEFT JOIN Teachers ON Courses.teacher_id = Teachers.teacher_id
    """)

    courses = cursor.fetchall()

    print("\nALL COURSES")
    print("-" * 50)

    if courses:
        for course in courses:
            print(f"Course ID: {course[0]} | Course: {course[1]} | Teacher: {course[2]}")
    else:
        print("No courses found. Please add a course first.")

#-------------------------------
# SEARCH COURSES
#-------------------------------

def search_course():
    course_name = input("Enter course name: ")

    cursor.execute("""
        SELECT Courses.course_id, Courses.course_name, Teachers.name
        FROM Courses
        LEFT JOIN Teachers ON Courses.teacher_id = Teachers.teacher_id
        WHERE Courses.course_name = ?
    """, (course_name,))

    course = cursor.fetchone()

    if course:
        print("\nCourse Found:")
        print(f"Course ID: {course[0]}")
        print(f"Course Name: {course[1]}")
        print(f"Teacher: {course[2]}")
    else:
        print("Course not found.")

#-------------------------------
#GRADE FUNCTIONS
#-------------------------------


#-------------------------------
# ADD GRADES
#-------------------------------

def add_grade():
    try:
        student_id = int(input("Student ID: "))
        course_id = int(input("Course ID: "))
        score = int(input("Score: "))
    except ValueError:
        print("Invalid input. Use numbers only.")
        return

    if score < 0 or score > 100:
        print("Score must be between 0 and 100.")
        return

    cursor.execute("""
        INSERT INTO Grades(student_id, course_id, score)
        VALUES (?, ?, ?)
    """, (student_id, course_id, score))

    conn.commit()
    print("Grade added successfully!\n")



#-------------------------------
# VIEW GRADES
#-------------------------------

def view_grades():
    cursor.execute("""
        SELECT Students.name, Courses.course_name, Grades.score
        FROM Grades
        JOIN Students ON Grades.student_id = Students.student_id
        JOIN Courses ON Grades.course_id = Courses.course_id
    """)

    grades = cursor.fetchall()

    print("\nALL GRADES")
    print("-" * 50)

    if grades:
        for grade in grades:
            print(f"Student: {grade[0]} | Course: {grade[1]} | Score: {grade[2]}")
    else:
        print("No grades found.")


#-------------------------------
# ATTENDANCE FUNCTIONS
#-------------------------------

#-------------------------------
# MARK ATTENDANCE
#------------------------------


def mark_attendance():
    try:
        student_id = int(input("Student ID: "))
        course_id = int(input("Course ID: "))
    except ValueError:
        print("Invalid input. Use numbers only.")
        return

    attendance_date = input("Date (YYYY-MM-DD): ")
    status = input("Status (Present/Absent): ")

    if status not in ["Present", "Absent"]:
        print("Status must be Present or Absent.")
        return

    cursor.execute("""
        INSERT INTO Attendance(student_id, course_id, attendance_date, status)
        VALUES (?, ?, ?, ?)
    """, (student_id, course_id, attendance_date, status))

    conn.commit()
    print("Attendance marked successfully!\n")

#-------------------------------
# VIEW ATTENDANCE
#-------------------------------


def view_attendance():
    cursor.execute("""
        SELECT Students.name, Courses.course_name, Attendance.attendance_date, Attendance.status
        FROM Attendance
        JOIN Students ON Attendance.student_id = Students.student_id
        JOIN Courses ON Attendance.course_id = Courses.course_id
    """)

    records = cursor.fetchall()

    print("\nATTENDANCE RECORDS")
    print("-" * 60)

    if records:
        for record in records:
            print(f"Student: {record[0]} | Course: {record[1]} | Date: {record[2]} | Status: {record[3]}")
    else:
        print("No attendance records found.")   

#-------------------------------
#  REPORT FUNCTIONS
#------------------------------- 

#-------------------------------
#  STUDENT PERFORMANCE REPORT
#-------------------------------

def generate_performance_report():
    cursor.execute("""
        SELECT Students.name, Courses.course_name, Grades.score
        FROM Grades
        JOIN Students ON Grades.student_id = Students.student_id
        JOIN Courses ON Grades.course_id = Courses.course_id
        ORDER BY Students.name, Courses.course_name
    """)

    grades = cursor.fetchall()

    print("\nPERFORMANCE REPORT")
    print("-" * 60)

    if grades:
        current_student = None
        for grade in grades:
            if grade[0] != current_student:
                if current_student is not None:
                    print()
                current_student = grade[0]
                print(f"\nStudent: {grade[0]}")
            print(f"  Course: {grade[1]} | Score: {grade[2]}")
    else:
        print("No grades found.")
#------------------------------------
#STUDENT REPORT FILE
#------------------------------------

def generate_student_report_file():
    create_reports_folder()

    try:
        student_id = int(input("Enter Student ID: "))
    except ValueError:
        print("Invalid Student ID.")
        return

    cursor.execute("""
        SELECT name, course, age, email
        FROM Students
        WHERE student_id = ?
    """, (student_id,))

    student = cursor.fetchone()

    if not student:
        print("Student not found.")
        return

    cursor.execute("""
        SELECT Courses.course_name, Grades.score
        FROM Grades
        JOIN Courses ON Grades.course_id = Courses.course_id
        WHERE Grades.student_id = ?
    """, (student_id,))

    grades = cursor.fetchall()

    cursor.execute("""
        SELECT attendance_date, status
        FROM Attendance
        WHERE student_id = ?
    """, (student_id,))

    attendance = cursor.fetchall()

    if grades:
        total = sum(score for _, score in grades)
        average = total / len(grades)

        if average >= 80:
            grade_letter = "A"
            remark = "Excellent"
        elif average >= 70:
            grade_letter = "B"
            remark = "Very Good"
        elif average >= 60:
            grade_letter = "C"
            remark = "Good"
        elif average >= 50:
            grade_letter = "D"
            remark = "Pass"
        else:
            grade_letter = "F"
            remark = "Needs Improvement"
    else:
        average = 0
        grade_letter = "N/A"
        remark = "No grades recorded"

    if attendance:
        present_count = sum(1 for record in attendance if record[1] == "Present")
        attendance_rate = (present_count / len(attendance)) * 100
    else:
        present_count = 0
        attendance_rate = 0

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    clean_name = student[0].replace(" ", "_")
    filename = f"Reports/{clean_name}_Student_Report_{timestamp}.txt"

    with open(filename, "w") as file:
        file.write("STUDENT PERFORMANCE REPORT\n")
        file.write("=" * 45 + "\n\n")

        file.write("STUDENT DETAILS\n")
        file.write("-" * 45 + "\n")
        file.write(f"Name   : {student[0]}\n")
        file.write(f"Course : {student[1]}\n")
        file.write(f"Age    : {student[2]}\n")
        file.write(f"Email  : {student[3]}\n\n")

        file.write("GRADES\n")
        file.write("-" * 45 + "\n")
        if grades:
            for course_name, score in grades:
                file.write(f"{course_name}: {score}\n")
        else:
            file.write("No grades recorded.\n")

        file.write("\nPERFORMANCE SUMMARY\n")
        file.write("-" * 45 + "\n")
        file.write(f"Average Score   : {average:.2f}\n")
        file.write(f"Grade           : {grade_letter}\n")
        file.write(f"Remark          : {remark}\n\n")

        file.write("ATTENDANCE SUMMARY\n")
        file.write("-" * 45 + "\n")
        file.write(f"Present Days     : {present_count}\n")
        file.write(f"Total Attendance : {len(attendance)}\n")
        file.write(f"Attendance Rate  : {attendance_rate:.2f}%\n")

    print(f"Student report saved as: {filename}")

#-------------------------------
# ATTENDANCE REPORT FILE
#------------------------------

def generate_attendance_report_file():
    create_reports_folder()

    try:
        student_id = int(input("Enter Student ID: "))
    except ValueError:
        print("Invalid Student ID.")
        return

    cursor.execute("SELECT name FROM Students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()

    if not student:
        print("Student not found.")
        return

    cursor.execute("""
        SELECT Courses.course_name, Attendance.attendance_date, Attendance.status
        FROM Attendance
        JOIN Courses ON Attendance.course_id = Courses.course_id
        WHERE Attendance.student_id = ?
        ORDER BY Attendance.attendance_date
    """, (student_id,))

    records = cursor.fetchall()

    if not records:
        print("No attendance records found for this student.")
        return

    present_count = sum(1 for record in records if record[2] == "Present")
    attendance_rate = (present_count / len(records)) * 100

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    clean_name = student[0].replace(" ", "_")
    filename = f"Reports/{clean_name}_Attendance_Report_{timestamp}.txt"

    with open(filename, "w") as file:
        file.write("ATTENDANCE REPORT\n")
        file.write("=" * 40 + "\n\n")
        file.write(f"Student Name: {student[0]}\n\n")

        file.write("ATTENDANCE RECORDS\n")
        file.write("-" * 40 + "\n")

        for course_name, date, status in records:
            file.write(f"{date} | {course_name} | {status}\n")

        file.write("\nSUMMARY\n")
        file.write("-" * 40 + "\n")
        file.write(f"Present Days    : {present_count}\n")
        file.write(f"Total Records   : {len(records)}\n")
        file.write(f"Attendance Rate : {attendance_rate:.2f}%\n")

    print(f"Attendance report saved as: {filename}")

#-------------------------------
#  TEACHER REPORT FILE
#-------------------------------    

def generate_teacher_report_file():
    create_reports_folder()

    try:
        teacher_id = int(input("Enter Teacher ID: "))
    except ValueError:
        print("Invalid Teacher ID.")
        return

    cursor.execute("""
        SELECT name, subject, email
        FROM Teachers
        WHERE teacher_id = ?
    """, (teacher_id,))

    teacher = cursor.fetchone()

    if not teacher:
        print("Teacher not found.")
        return

    cursor.execute("""
        SELECT course_name
        FROM Courses
        WHERE teacher_id = ?
    """, (teacher_id,))

    courses = cursor.fetchall()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    clean_name = teacher[0].replace(" ", "_")
    filename = f"Reports/{clean_name}_Teacher_Report_{timestamp}.txt"

    with open(filename, "w") as file:
        file.write("TEACHER REPORT\n")
        file.write("=" * 40 + "\n\n")

        file.write("TEACHER DETAILS\n")
        file.write("-" * 40 + "\n")
        file.write(f"Name    : {teacher[0]}\n")
        file.write(f"Subject : {teacher[1]}\n")
        file.write(f"Email   : {teacher[2]}\n\n")

        file.write("ASSIGNED COURSES\n")
        file.write("-" * 40 + "\n")

        if courses:
            for course in courses:
                file.write(f"- {course[0]}\n")
        else:
            file.write("No courses assigned.\n")

    print(f"Teacher report saved as: {filename}")

#----------------------------------
#COURSE REPORT FILE
#-----------------------------------

def generate_course_report_file():
    create_reports_folder()

    try:
        course_id = int(input("Enter Course ID: "))
    except ValueError:
        print("Invalid Course ID.")
        return

    cursor.execute("""
        SELECT Courses.course_name, Teachers.name
        FROM Courses
        LEFT JOIN Teachers ON Courses.teacher_id = Teachers.teacher_id
        WHERE Courses.course_id = ?
    """, (course_id,))

    course = cursor.fetchone()

    if not course:
        print("Course not found.")
        return

    cursor.execute("""
        SELECT name, email
        FROM Students
        WHERE course = ?
    """, (course[0],))

    students = cursor.fetchall()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    clean_course = course[0].replace(" ", "_")
    filename = f"Reports/{clean_course}_Course_Report_{timestamp}.txt"

    with open(filename, "w") as file:
        file.write("COURSE REPORT\n")
        file.write("=" * 40 + "\n\n")

        file.write("COURSE DETAILS\n")
        file.write("-" * 40 + "\n")
        file.write(f"Course Name : {course[0]}\n")
        file.write(f"Teacher     : {course[1]}\n\n")

        file.write("STUDENTS ENROLLED\n")
        file.write("-" * 40 + "\n")

        if students:
            for student in students:
                file.write(f"- {student[0]} | {student[1]}\n")
        else:
            file.write("No students enrolled in this course.\n")

    print(f"Course report saved as: {filename}")

#-------------------------------
# BACKUP DATABASE
#------------------------------

def backup_database():
    create_backups_folder()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = f"Backups/education_management_backup_{timestamp}.db"

    conn.commit()

    shutil.copy("education_management.db", backup_file)

    print(f"Database backup created successfully: {backup_file}")

#-------------------------------
# STUDENT PERFORMANCE SUMMARY   
#-------------------------------

def student_performance_summary():
    try:
        student_id = int(input("Enter Student ID: "))
    except ValueError:
        print("Invalid Student ID.")
        return

    cursor.execute("SELECT name FROM Students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()

    if not student:
        print("Student not found.")
        return

    cursor.execute("""
        SELECT score FROM Grades
        WHERE student_id = ?
    """, (student_id,))

    scores = cursor.fetchall()

    if scores:
        total = sum(score[0] for score in scores)
        average = total / len(scores)

        if average >= 80:
            grade = "A"
            remark = "Excellent"
        elif average >= 70:
            grade = "B"
            remark = "Very Good"
        elif average >= 60:
            grade = "C"
            remark = "Good"
        elif average >= 50:
            grade = "D"
            remark = "Pass"
        else:
            grade = "F"
            remark = "Needs Improvement"
    else:
        average = 0
        grade = "N/A"
        remark = "No grades recorded"

    cursor.execute("""
        SELECT status FROM Attendance
        WHERE student_id = ?
    """, (student_id,))

    attendance = cursor.fetchall()

    if attendance:
        present_count = sum(1 for record in attendance if record[0] == "Present")
        total_attendance = len(attendance)
        attendance_rate = (present_count / total_attendance) * 100
    else:
        present_count = 0
        total_attendance = 0
        attendance_rate = 0

    print("\n===== STUDENT PERFORMANCE SUMMARY =====")
    print(f"Student Name      : {student[0]}")
    print(f"Average Score     : {average:.2f}")
    print(f"Grade             : {grade}")
    print(f"Remark            : {remark}")
    print(f"Present Days      : {present_count}")
    print(f"Total Attendance  : {total_attendance}")
    print(f"Attendance Rate   : {attendance_rate:.2f}%")

#-------------------------------
# VIEW GENERATED REPORTS
#------------------------------

def view_generated_reports():
    create_reports_folder()

    reports = os.listdir("Reports")

    print("\nGENERATED REPORTS")
    print("-" * 40)

    if reports:
        for report in reports:
            print(report)
    else:
        print("No reports generated yet.")



#-------------------------------
# SYSTEM SUMMARY
#-------------------------------

def system_summary():
    # Count students
    cursor.execute("SELECT COUNT(*) FROM Students")
    total_students = cursor.fetchone()[0]

    # Count teachers
    cursor.execute("SELECT COUNT(*) FROM Teachers")
    total_teachers = cursor.fetchone()[0]

    # Count courses
    cursor.execute("SELECT COUNT(*) FROM Courses")
    total_courses = cursor.fetchone()[0]

    # Count grades
    cursor.execute("SELECT COUNT(*) FROM Grades")
    total_grades = cursor.fetchone()[0]

    # Count attendance records
    cursor.execute("SELECT COUNT(*) FROM Attendance")
    total_attendance = cursor.fetchone()[0]

    print("\n========== SYSTEM SUMMARY ==========")
    print(f"Total Students          : {total_students}")
    print(f"Total Teachers          : {total_teachers}")
    print(f"Total Courses           : {total_courses}")
    print(f"Total Grades Recorded   : {total_grades}")
    print(f"Attendance Records      : {total_attendance}")

#-------------------------------
# GENERATE SYSTEM SUMMARY REPORT
#-------------------------------

def generate_system_summary_report():
    create_reports_folder()

    cursor.execute("SELECT COUNT(*) FROM Students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Teachers")
    total_teachers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Courses")
    total_courses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Grades")
    total_grades = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Attendance")
    total_attendance = cursor.fetchone()[0]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Reports/System_Summary_{timestamp}.txt"

    with open(filename, "w") as file:
        file.write("SYSTEM SUMMARY REPORT\n")
        file.write("=" * 40 + "\n\n")
        file.write(f"Total Students        : {total_students}\n")
        file.write(f"Total Teachers        : {total_teachers}\n")
        file.write(f"Total Courses         : {total_courses}\n")
        file.write(f"Total Grades Recorded : {total_grades}\n")
        file.write(f"Attendance Records    : {total_attendance}\n")
        file.write("\nReport generated successfully.\n")

    print(f"System summary report saved as: {filename}")


# -------------------------------
# LOGIN SYSTEM
# -------------------------------
def login():
    print("\n===== LOGIN =====")
    username = input("Username: ")
    password = input("Password: ")

    hashed_password = hash_password(password)

    cursor.execute("""
        SELECT role, username FROM Users
        WHERE username = ? AND password = ?
    """, (username, hashed_password))

    result = cursor.fetchone()

    if result:
        print(f"\nLogin successful! Role: {result[0]}")
        return result[0], result[1]
    else:
        print("Invalid credentials.")
        return None, None

#---------------------------------
#CHANGE PASSWORD
#--------------------------------

def change_password(username):
    print("\n===== CHANGE PASSWORD =====")

    current_password = input("Enter current password: ")
    new_password = input("Enter new password: ")
    confirm_password = input("Confirm new password: ")

    if new_password != confirm_password:
        print("New passwords do not match.")
        return

    hashed_current = hash_password(current_password)

    cursor.execute("""
        SELECT * FROM Users
        WHERE username = ? AND password = ?
    """, (username, hashed_current))

    user = cursor.fetchone()

    if not user:
        print("Current password is incorrect.")
        return

    hashed_new = hash_password(new_password)

    cursor.execute("""
        UPDATE Users
        SET password = ?
        WHERE username = ?
    """, (hashed_new, username))

    conn.commit()
    print("Password changed successfully!\n")

# -------------------------------
# ADMIN MENU
#--------------------------------
def admin_menu(username):
    while True:
        print("\n===== ADMIN DASHBOARD =====")
        print("1. Add Student")
        print("2. View Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Add Teacher")
        print("7. View Teachers")
        print("8. Search Teacher")
        print("9. Update Teacher")
        print("10. Delete Teacher")
        print("11. Add Course")
        print("12. View Courses")
        print("13. Search Course")
        print("14. Add Grade")
        print("15. View Grades")
        print("16. Generate Performance Report")
        print("18. Mark Attendance")
        print("19. View Attendance")
        print("20. Student Performance Summary")
        print("21. View System Summary")
        print("22. Generate Summary Report")
        print("23. Generate Student Report File")
        print("24. Generate Attendance Report File")
        print("25. Generate Teacher Report File")
        print("26. Generate Course Report File")
        print("27. View generated reports")
        print("28. Change password")
        print("29. Backup Database")
        print("30. Logout")
        choice = input("Select: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            update_student()
        elif choice == "5":
            delete_student()
        elif choice == "6":
            add_teacher()
        elif choice == "7":
            view_teachers()
        elif choice == "8":
            search_teacher()
        elif choice == "9":
            update_teacher()
        elif choice == "10":
            delete_teacher()
        elif choice == "11":
            add_course()
        elif choice == "12":
            view_courses()
        elif choice == "13":
            search_course()
        elif choice == "14":
            add_grade()
        elif choice == "15":
            view_grades()
        elif choice == "16":
            generate_performance_report()
        elif choice == "18":
            mark_attendance()
        elif choice == "19":
            view_attendance()
        elif choice == "20":
            student_performance_summary()
        elif choice == "21":
            system_summary()
        elif choice == "22":
            generate_system_summary_report()
        elif choice == "23":
            generate_student_report_file()
        elif choice == "24":
            generate_attendance_report_file()
        elif choice == "25":
            generate_teacher_report_file()
        elif choice == "26":
            generate_course_report_file()
        elif choice == "27":
            view_generated_reports()
        elif choice == "28":
            change_password(username)
        elif choice == "29":
            backup_database()
        elif choice == "30":
            print("Logging out...")
            break
        else:
            print("Invalid option.")


# -------------------------------
# TEACHER MENU
# -------------------------------
def teacher_menu(username):
    while True:
        print("\n===== TEACHER DASHBOARD =====")
        print("1. View Students")
        print("2. Search Student")
        print("3. Add Teacher")
        print("4. View Teachers")
        print("5. Search Teacher")
        print("6. View Courses")
        print("7. Search Course")
        print("8. Add Grade")
        print("9. View Grades")
        print("10. Generate Performance Report")
        print("11. Mark Attendance")
        print("12. View Attendance")
        print("13. Student Performance Summary")
        print("14. Generate Summary Report")
        print("15. Generate Student Report File")
        print("16. Generate Attendance Report File")
        print("17. Change password")
        print("18. Logout")

        choice = input("Select: ")

        if choice == "1":
            view_students()
        elif choice == "2":
            search_student()
        elif choice == "3":
            handle_add_teacher("teacher")
        elif choice == "4":
            view_teachers()
        elif choice == "5":
            search_teacher()
        elif choice == "6":
            view_courses()
        elif choice == "7":
            search_course()
        elif choice == "8":
            add_grade()
        elif choice == "9":
            view_grades()
        elif choice == "10":
            generate_performance_report()
        elif choice == "11":
            mark_attendance()
        elif choice == "12":
            view_attendance()
        elif choice == "13":
            student_performance_summary()
        elif choice == "14":
            generate_system_summary_report()
        elif choice == "15":
            generate_student_report_file()
        elif choice == "16":
            generate_attendance_report_file()
        elif choice == "17":
            change_password(username)
        elif choice == "18":
            print("Logging out...")
            break
        else:
            print("Invalid option.")


# -------------------------------
# STUDENT MENU
# -------------------------------
def student_menu(username):
    while True:
        print("\n===== STUDENT DASHBOARD =====")
        print("1. View My Details")
        print("2. View Courses")
        print("3. Student Performance Summary")
        print("4. Change password")
        print("5. Logout")

        choice = input("Select: ")

        if choice == "1":
            view_my_details(username)
        elif choice == "2":
            view_courses()
        elif choice == "3":
            student_performance_summary()
        elif choice == "4":
            change_password(username)
        elif choice == "5":
            print("Logging out...")
            break
        else:
            print("Invalid option.")

# -------------------------------
# START SYSTEM
# -------------------------------
def start_system():
    role, username = login()

    if role == "admin":
        admin_menu(username)
    elif role == "teacher":
        teacher_menu(username)
    elif role == "student":
        student_menu(username)
    else:
        print("Access denied.")


#-------------------------------
# RUN PROGRAM
#-------------------------------

start_system()

conn.close()

