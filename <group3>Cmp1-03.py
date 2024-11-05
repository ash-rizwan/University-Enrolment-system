import re               # For regular expressions in email and password validation
import random           # For generating random subject IDs and marks
import pickle           # For file storage of student data
import os               # To check file existence
import tkinter as tk    # For GUI interface
from tkinter import messagebox  # For GUI message boxes


class Student:
    def __init__(self, name, email, password):
        self.id = f"{random.randint(1, 999999):06}"  # Unique 6-digit ID
        self.name = name
        self.email = email
        self.password = password
        self.subjects = []  # List to store subjects

    def enroll_subject(self):
        """Enrolls the student in a new subject with a unique ID if they haven't exceeded 4 subjects."""
        if len(self.subjects) >= 4:
            return None

        # Create a new Subject instance
        new_subject = Subject()

        # Check if the subject ID is unique within the student's subjects
        existing_subject_ids = {subj['id'] for subj in self.subjects}
        while new_subject.id in existing_subject_ids:
            new_subject = Subject()  # Generate a new Subject if there's a duplicate ID

        # Add the unique subject to the student's list
        subject_info = {
            'id': new_subject.id,
            'mark': new_subject.mark,
            'grade': new_subject.grade
        }
        self.subjects.append(subject_info)
        return subject_info

    def drop_subject(self, subject_id):
        """Removes a subject from the student's list of subjects by subject ID."""
        self.subjects = [subject for subject in self.subjects if subject['id'] != subject_id]

    def calculate_average_mark(self):
        """Calculates the average mark of all enrolled subjects."""
        if not self.subjects:
            return 0
        total_marks = sum(subject['mark'] for subject in self.subjects)
        return total_marks / len(self.subjects)

    def is_passing(self):
        """Checks if the student is passing based on an average mark of 50 or more."""
        return self.calculate_average_mark() >= 50

    def change_password(self, new_password):
        """Changes the student's password."""
        self.password = new_password

class Subject:
    def __init__(self):
        self.id = f"{random.randint(1, 999):03}"  # Unique 3-digit ID
        self.mark = random.randint(25, 100)       # Random mark between 25 and 100
        self.grade = self.assign_grade(self.mark) # Assign grade based on the mark

    def assign_grade(self, mark):
        """Assigns a grade based on the UTS grading system."""
        if mark < 50:
            return "Z"
        elif 50 <= mark < 65:
            return "P"
        elif 65 <= mark < 75:
            return "C"
        elif 75 <= mark < 85:
            return "D"
        else:  # mark >= 85
            return "HD"


class Database:
    def __init__(self, filename="students.data"):
        self.filename = filename
        self.check_file_exists()

    def check_file_exists(self):
        """Check if students.data file exists; create it if not."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                pickle.dump({}, f)  # Initialize with an empty dictionary

    def save_data(self, data):
        """Write objects to students.data."""
        with open(self.filename, 'wb') as f:
            pickle.dump(data, f)

    def load_data(self):
        """Read objects from students.data."""
        with open(self.filename, 'rb') as f:
            return pickle.load(f)

    def clear_data(self):
        """Clear all objects from students.data."""
        with open(self.filename, 'wb') as f:
            pickle.dump({}, f)  # Reset to an empty dictionary


class StudentController:
    def __init__(self, database):
        self.database = database  # Instance of the Database class

    def _is_valid_email(self, email):
        """Validates that the email has the format firstname.lastname@university.com."""
        return re.match(r"^[a-zA-Z]+\.[a-zA-Z]+@university\.com$", email) is not None

    def _is_valid_password(self, password):
        """Validates that the password starts with an uppercase letter, has at least five letters, and ends with three or more digits."""
        return re.match(r"^[A-Z][a-zA-Z]{4,}\d{3,}$", password) is not None

    def login_student(self, email, password):
        """Logs in a student if email and password match."""
        data = self.database.load_data()  # Load data from students.data

        # Check for valid email and password format
        if not self._is_valid_email(email) or not self._is_valid_password(password):
            return"\033[91mIncorrect email or password format.\033[0m"


        # If the email format is correct but the student does not exist in the database
        if email not in data:
            return "\033[93mEmail and password formats acceptable.\033[0m\n\033[91mStudent does not exist.\033[0m"

        # Check if the provided password matches the stored password
        if data[email].password == password:
            print("\033[93mLogin successful.\033[0m")  # Yellow for success
            return data[email]
        else:
            # Print a single notification for an incorrect password
            return"\033[91mIncorrect email or password format.\033[0m"


    def change_student_password(self, student, new_password):
        """Changes the student's password with confirmation and validation."""
        # Validate the new password format
        if not self._is_valid_password(new_password):
            print(
                "\033[91mInvalid password format. Must start with an uppercase letter, contain at least five letters, and end with three or more digits.\033[0m")
            return

            # Set the new password and save to the database
        student.password = new_password
        data = self.database.load_data()
        data[student.email] = student
        self.database.save_data(data)

    def generate_student_id(self):
        """Generates a unique 6-digit student ID with leading zeros."""
        data = self.database.load_data()
        existing_ids = {student.id for student in data.values()}  # Set of IDs already in the database

        while True:
            student_id = f"{random.randint(1, 999999):06}"
            if student_id not in existing_ids:
                return student_id

    def register_student(self, name, email, password):
        """Registers a new student if email and password are valid and the email is not already in use."""
        # Load existing data and check for existing student
        data = self.database.load_data()

        # Check if the email already exists in the database
        if email in data:
            print("\033[91mStudent already exists.\033[0m")  # Red color for existence error
            return None

        # Create and save the new student
        student_id = self.generate_student_id()
        student = Student(name, email, password)
        student.id = student_id  # Assign the generated student ID
        data[email] = student
        self.database.save_data(data)
        return student


class SubjectController:
    def __init__(self, database):
        self.database = database  # Instance of the Database class

    def enroll_subject(self, student):
        """Enrolls the student in a new subject if they haven't reached the limit."""
        subject_info = student.enroll_subject()

        if subject_info is None:
            print("\033[91mStudents are allowed to enrol in 4 subjects only.\033[0m")
            return

        # Print enrollment confirmation
        print(f"\033[93mEnrolling in Subject-{subject_info['id']}\033[0m")
        print(f"\033[93mYou are now enrolled in {len(student.subjects)} out of 4 subjects.\033[0m")

        # Update the student data in the database
        data = self.database.load_data()
        data[student.email] = student
        self.database.save_data(data)

    def remove_subject(self, student, subject_id):
        """Removes a subject from the student's enrolled subjects by subject ID."""
        if not any(subj['id'] == subject_id for subj in student.subjects):
            print(f"Subject {subject_id} not found.")
            return

        student.drop_subject(subject_id)

        # Update the student in the database
        data = self.database.load_data()
        data[student.email] = student
        self.database.save_data(data)
        print(f"\033[93mDropping Subject-{subject_id}\033[0m")
        print(f"\033[93mYou are now enrolled in {len(student.subjects)} out of 4 subjects\033[0m")


    def show_enrolled_subjects(self, student):
        """Displays all enrolled subjects for a student."""
        subjects = student.subjects
        print(f"\033[93mShowing {len(subjects)} subjects\033[0m")

        if not subjects:
            print("\033[93mShowing 0 subjects\033[0m")
        else:
            for subject in subjects:
                print(f"[ Subject::{subject['id']} -- mark = {subject['mark']} -- grade = {subject['grade']} ]")


class AdminController:
    def __init__(self, database):
        self.database = database  # Instance of the Database class
        self.subject = Subject()


    def show_all_students(self):
        """Displays all registered students and their details."""
        data = self.database.load_data()
        if not data:
            return "\033[93mStudent List\033[0m\n   < Nothing to Display >"
        else:
            output = ["\033[93mStudent List\033[0m"]
            for email, student in data.items():
                output.append(f"{student.name} :: {student.id} --> Email: {email}")
            return "\n".join(output)

    def group_students_by_grade(self):
        """Groups students based on the average grade across their subjects."""
        data = self.database.load_data()
        groups = {"HD": [], "D": [], "C": [], "P": [], "Z": []}

        for email, student in data.items():
            avg_mark = student.calculate_average_mark()
            grade = self.subject.assign_grade(avg_mark)
            groups[grade].append((student.name, student.id, grade, avg_mark))

        for grade, students in groups.items():
            if students:
                student_list = ", ".join(
                    [f"{name} :: {student_id} --> GRADE: {grade} - MARK: {mark:.2f}" for name, student_id, grade, mark
                     in students]
                )
                print(f"   {grade}  --> [{student_list}]")
            else:
                print(f"   {grade}  --> [< Nothing to Display >]")

    def partition_students_pass_fail(self):
        """Partitions students into PASS or FAIL based on their average mark."""
        data = self.database.load_data()
        passed, failed = [], []
        for email, student in data.items():
            avg_mark = student.calculate_average_mark()
            if student.is_passing():
                passed.append((student.name, student.id, avg_mark))
            else:
                failed.append((student.name, student.id, avg_mark))

        print("FAIL --> [{}]".format(
            ", ".join([f"{name} :: {student_id} --> MARK: {mark:.2f}" for name, student_id, mark in failed])))
        print("PASS --> [{}]".format(
            ", ".join([f"{name} :: {student_id} --> MARK: {mark:.2f}" for name, student_id, mark in passed])))

    def remove_student(self, student_id):
        """Removes an individual student by ID."""
        data = self.database.load_data()
        to_remove = [email for email, student in data.items() if student.id == student_id]

        if to_remove:
            del data[to_remove[0]]
            self.database.save_data(data)
            return True
        else:
            return False

    def clear_all_student_data(self):
        """Clears all student data from the database."""
        self.database.clear_data()
        print("\033[93mAll student data has been cleared.\033[0m")


class GUIUniApp:
    def __init__(self, student_controller, subject_controller):
        self.student_controller = student_controller
        self.subject_controller = subject_controller
        self.logged_in_student = None  # Stores the currently logged-in student

        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("GUIUniApp - Login")
        self.root.geometry("400x300")

        # Start with the login window
        self.login_window()

    def login_window(self):
        """Main login window for students."""
        self.clear_window()

        tk.Label(self.root, text="Student Login", font=("Arial", 14)).pack(pady=20)

        tk.Label(self.root, text="Email:").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.submit_login).pack(pady=10)
        tk.Button(self.root, text="Register", command=self.register_window).pack(pady=5)  # Registration button

    def register_window(self):
        """Registration window for new students."""
        self.clear_window()

        tk.Label(self.root, text="Student Registration", font=("Arial", 14)).pack(pady=20)

        tk.Label(self.root, text="Name:").pack()
        name_entry = tk.Entry(self.root)
        name_entry.pack()

        tk.Label(self.root, text="Email:").pack()
        email_entry = tk.Entry(self.root)
        email_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        password_entry = tk.Entry(self.root, show="*")
        password_entry.pack()

        def submit_registration():
            name = name_entry.get()
            email = email_entry.get()
            password = password_entry.get()

            if not self.student_controller._is_valid_email(email):
                messagebox.showerror("Error", "Invalid email format. Use firstname.lastname@university.com.")
                return
            if not self.student_controller._is_valid_password(password):
                messagebox.showerror("Error", "Invalid password format.")
                return

            student = self.student_controller.register_student(name, email, password)
            if student:
                messagebox.showinfo("Success", "Registration successful!")
                self.login_window()
            else:
                messagebox.showerror("Error", "Registration failed. Student may already exist.")

        tk.Button(self.root, text="Register", command=submit_registration).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.login_window).pack(pady=5)

    def submit_login(self):
        """Handles login submission and checks student credentials."""
        email = self.email_entry.get()
        password = self.password_entry.get()

        # Validate fields
        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password.")
            return

        if not re.match(r"^[a-zA-Z]+\.[a-zA-Z]+@university\.com$", email):
            messagebox.showerror("Error", "Invalid email format. Use firstname.lastname@university.com.")
            return

        # Attempt login
        student = self.student_controller.login_student(email, password)
        if isinstance(student, Student):
            messagebox.showinfo("Success", "Login Successful")
            self.logged_in_student = student
            self.main_menu_window()
        else:
            messagebox.showerror("Error", "Invalid email or password.")
            self.logged_in_student = None

    def main_menu_window(self):
        """Main menu window shown after successful login."""
        self.clear_window()


        tk.Label(self.root, text="Main Menu", font=("Arial", 14)).pack(pady=20)

        tk.Button(self.root, text="Enroll in a Subject", command=self.enrollment_window, width=20).pack(pady=5)
        tk.Button(self.root, text="Show Enrolled Subjects", command=self.subject_list_window, width=20).pack(pady=5)
        tk.Button(self.root, text="Change Password", command=self.change_password_window, width=20).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.logout, width=20).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.root.quit, width=20).pack(pady=5)

    def enrollment_window(self):
        """Window to enroll in a subject, ensuring a max of 4 subjects."""
        if len(self.logged_in_student.subjects) >= 4:
            messagebox.showerror("Error", "Cannot enroll in more than 4 subjects.")
            return

        self.clear_window()

        tk.Label(self.root, text="Enroll in a Subject", font=("Arial", 14)).pack(pady=20)

        tk.Button(self.root, text="Enroll", command=self.enroll_subject, width=20).pack(pady=10)
        tk.Button(self.root, text="Back to Main Menu", command=self.main_menu_window, width=20).pack(pady=5)

    def enroll_subject(self):
        """Handles subject enrollment, adds a new subject to the student’s list."""
        # Create a new subject and enroll
        self.subject_controller.enroll_subject(self.logged_in_student)
        messagebox.showinfo("Success", "Enrolled in a new subject.")
        self.main_menu_window()

    def subject_list_window(self):
        """Displays the list of subjects the student is enrolled in with an option to remove."""
        self.clear_window()

        tk.Label(self.root, text="Enrolled Subjects", font=("Arial", 14)).pack(pady=20)

        subjects = self.logged_in_student.subjects
        if not subjects:
            tk.Label(self.root, text="No subjects enrolled.").pack()
        else:
            for subject in subjects:
                subject_info = f"ID: {subject['id']}, Mark: {subject['mark']}, Grade: {subject['grade']}"
                tk.Label(self.root, text=subject_info).pack()

        tk.Label(self.root, text="Enter Subject ID to Remove:").pack(pady=10)
        subject_id_entry = tk.Entry(self.root)
        subject_id_entry.pack()

        def remove_subject():
            subject_id = subject_id_entry.get().strip()  # Get and strip any whitespace

            # Check if the subject ID is provided
            if not subject_id:
                messagebox.showerror("Error", "Please enter a Subject ID.")
                return

            # Check if the subject ID exists in the student's enrolled subjects
            if not any(subj['id'] == subject_id for subj in self.logged_in_student.subjects):
                messagebox.showerror("Error", f"Subject {subject_id} not found.")
                return

            # If subject ID is valid, proceed to remove
            self.subject_controller.remove_subject(self.logged_in_student, subject_id)
            messagebox.showinfo("Success", f"Subject {subject_id} removed.")
            self.subject_list_window()

        tk.Button(self.root, text="Remove Subject", command=remove_subject, width=20).pack(pady=5)
        tk.Button(self.root, text="Back to Main Menu", command=self.main_menu_window, width=20).pack(pady=5)

    def change_password_window(self):
        """Window to change the logged-in student's password."""
        self.clear_window()

        tk.Label(self.root, text="Change Password", font=("Arial", 14)).pack(pady=20)

        tk.Label(self.root, text="New Password:").pack()
        new_password_entry = tk.Entry(self.root, show="*")
        new_password_entry.pack()

        tk.Label(self.root, text="Confirm Password:").pack()
        confirm_password_entry = tk.Entry(self.root, show="*")
        confirm_password_entry.pack()

        def submit_change_password():
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()

            if new_password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            if not self.student_controller._is_valid_password(new_password):
                messagebox.showerror("Error", "Invalid password format.")
                return

            self.student_controller.change_student_password(self.logged_in_student, new_password)
            messagebox.showinfo("Success", "Password changed successfully.")
            self.main_menu_window()

        tk.Button(self.root, text="Change Password", command=submit_change_password, width=20).pack(pady=10)
        tk.Button(self.root, text="Back to Main Menu", command=self.main_menu_window, width=20).pack(pady=5)

    def logout(self):
        """Logs out the student and returns to the login window."""
        self.logged_in_student = None
        self.login_window()

    def clear_window(self):
        """Clears all widgets from the main window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        """Starts the GUI main loop."""
        self.root.mainloop()


class UniversitySystem:
    def __init__(self):
        self.database = Database()  # Initializes the database
        self.student_controller = StudentController(self.database)
        self.subject_controller = SubjectController(self.database)
        self.admin_controller = AdminController(self.database)  # Only used for CLI mode

    def start(self):
        """Initializes the system and prompts the user to select CLI or GUI mode."""
        while True:
            choice = input("\033[94mSelect mode:\n(1) CLI\n(2) GUI\n(3) Exit\nChoice: \033[0m")
            if choice == '1':
                self.main_menu()  # Launch CLI mode
            elif choice == '2':
                gui_app = GUIUniApp(self.student_controller, self.subject_controller)
                gui_app.run()  # Launch GUIUniApp without admin options
            elif choice == '3':
                print(f"\033[93mThank You\033[0m")
                break
            else:
                print("Invalid choice.")

    def main_menu(self):
        """Displays the main university menu for CLI with options for Admin, Student, and Exit."""
        while True:
            print("\n\033[94m--- University System ---\033[0m")
            print("\033[94m(A)dmin, (S)tudent, or X\033[0m")
            choice = input("\033[94mPlease select an option: \033[0m").lower()

            if choice == 'a':
                self.admin_menu()
            elif choice == 's':
                self.student_menu()
            elif choice == 'x':
                print("\033[93mThank You\033[0m")
                exit()
            else:
                print("\033[93mInvalid option. Please try again.\033[0m")

    def student_menu(self):
        """Displays the student menu for login and registration with validation feedback."""
        while True:
            print("\n\033[94m--- Student System ---\033[0m")
            choice = input("\033[94m(l) login, (r) register, (x) exit\033[0m\nSelect an option: ").lower()

            if choice == 'l':
                print("\033[92mStudent Sign In\033[0m")
                email = input("\033[0mEnter email: ")
                password = input("\033[0mEnter password: ")
                login_result = self.student_controller.login_student(email, password)

                if isinstance(login_result, Student):
                    self.subject_menu(login_result)
                else:
                    # Print the single message returned from login_student
                    print(f"\033[91m{login_result}\033[0m")

            elif choice == 'r':
                print("\033[92mStudent Sign Up\033[0m")

                # Loop until a valid email is entered
                while True:
                    email = input("Enter email: ")
                    if self.student_controller._is_valid_email(email):
                        break
                    else:
                        print("\033[93mInvalid email format. Please use firstname.lastname@university.com format.\033[0m")

                # Loop until a valid password is entered
                while True:
                    password = input("Enter password: ")
                    if self.student_controller._is_valid_password(password):
                        print("\033[93mEmail and password formats acceptable.\033[0m")
                        break
                    else:
                        print(
                            "\033[91mInvalid password format. Password must start with an uppercase letter, contain at least five letters, and end with three or more digits.\033[0m")

                # Check if the student is already registered
                data = self.student_controller.database.load_data()
                if email in data:
                    print("\033[91mStudent already exists.\033[0m")
                    continue

                # Prompt for the student's name after email and password are validated
                name = input("\033[0mEnter name: ")

                # Register the student with validated inputs
                student = self.student_controller.register_student(name, email, password)
                if student:
                    print(f"\033[93mStudent {name} successfully registered with ID: {student.id}.\033[0m")

            elif choice == 'x':
                break
            else:
                print("Invalid option.")

    def subject_menu(self, student):
        """Displays the subject menu for managing subjects."""
        while True:
            print("\n\033[94m--- Subject Enrolment System ---\033[0m")
            choice = input("\033[94m(c) change password\n(e) enroll\n(r) remove\n(s) show\n(x) exit\033[0m\nSelect an option: ").lower()

            if choice == 'c':
                print("\n\033[93mUpdating Password\033[0m")
                new_password = input("\033[0mNew Password: \033[0m")

                # Loop until the new password and confirmation match
                while True:
                    confirm_password = input("\033[0mConfirm Password: \033[0m")

                    if new_password != confirm_password:
                        print("\033[91mPassword does not match - try again\033[0m")  # Red color for error
                    else:
                        # Passwords match, break out of the confirmation loop
                        break

                # Change the password after successful confirmation
                self.student_controller.change_student_password(student, new_password)
                print("\033[93mPassword updated successfully.\033[0m")

            elif choice == 'e':
                self.subject_controller.enroll_subject(student)
            elif choice == 'r':
                subject_id = input("\033[0mEnter subject ID to remove: \033[0m")
                self.subject_controller.remove_subject(student, subject_id)
            elif choice == 's':
                self.subject_controller.show_enrolled_subjects(student)
            elif choice == 'x':
                break
            else:
                print("\033[91mInvalid option.\033[0m")

    def admin_menu(self):
        """Displays the admin menu for various administrative actions."""
        while True:
            print("\n\033[94m--- Admin System (c/g/p/r/s/x) ---\033[0m")
            choice = input("\033[94mSelect an option: \033[0m").lower()

            if choice == 'c':
                # Confirm database clearing with yellow and red prompts
                print("\033[93mClearing students database\033[0m")
                confirm = input("\033[91mAre you sure you want to clear the database (Y)ES/(N)O: \033[0m").lower()
                if confirm == 'y':
                    self.admin_controller.clear_all_student_data()
                    print("\033[93mStudents data cleared\033[0m")
                else:
                    print("\033[93mClearing operation cancelled\033[0m")

            elif choice == 'g':
                print("\033[93mGrade Grouping\033[0m")
                self.admin_controller.group_students_by_grade()
            elif choice == 'p':
                print("\033[93mPASS/FAIL Partition\033[0m")
                self.admin_controller.partition_students_pass_fail()
            elif choice == 'r':
                student_id = input("Remove by ID: ")
                if self.admin_controller.remove_student(student_id):
                    print(f"\033[93mRemoving Student {student_id} Account\033[0m")
                else:
                    print(f"\033[91mStudent {student_id} does not exist\033[0m")
            elif choice == 's':
                result = self.admin_controller.show_all_students()
                print(result)

            elif choice == 'x':
                break
            else:
                print("\033[91mInvalid option.\033[0m")


if __name__ == "__main__":
    system = UniversitySystem()
    system.start()
