import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os


class Student:
    """Represents a single student."""

    def __init__(self, roll_no, name):
        self.roll_no = roll_no
        self.name = name
        self.attendance = "Absent"


class AttendanceSystem:
    """Handles student management and attendance logic."""

    def __init__(self):
        self.students = []

    def add_student(self, roll_no, name):
        # Check if roll number already exists
        for s in self.students:
            if s.roll_no == roll_no:
                raise ValueError("Roll number already exists!")
        self.students.append(Student(roll_no, name))

    def mark_attendance(self, roll_no, status):
        for s in self.students:
            if s.roll_no == roll_no:
                s.attendance = status
                return
        raise ValueError("Student not found!")

    def save_to_csv(self, filename="attendance.csv"):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Roll No", "Name", "Attendance"])
            for s in self.students:
                writer.writerow([s.roll_no, s.name, s.attendance])

    def load_from_csv(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError("File not found!")
        self.students.clear()
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                student = Student(row["Roll No"], row["Name"])
                student.attendance = row["Attendance"]
                self.students.append(student)


class AttendanceApp1:
    """Tkinter GUI for Attendance System."""

    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance System")
        self.system = AttendanceSystem()

        self.create_widgets()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="Student Attendance System", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        # Frame for adding student
        frame_add = tk.LabelFrame(self.root, text="Add Student", padx=10, pady=10)
        frame_add.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_add, text="Roll No:").grid(row=0, column=0, padx=5, pady=5)
        self.roll_entry = tk.Entry(frame_add)
        self.roll_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_add, text="Name:").grid(row=0, column=2, padx=5, pady=5)
        self.name_entry = tk.Entry(frame_add)
        self.name_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(frame_add, text="Add Student", command=self.add_student).grid(row=0, column=4, padx=10)

        # Frame for attendance
        frame_table = tk.LabelFrame(self.root, text="Mark Attendance", padx=10, pady=10)
        frame_table.pack(fill="both", expand=True, padx=20, pady=10)

        # Treeview
        columns = ("roll", "name", "attendance")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")
        self.tree.heading("roll", text="Roll No")
        self.tree.heading("name", text="Name")
        self.tree.heading("attendance", text="Attendance")

        self.tree.pack(fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Mark Present", command=lambda: self.update_attendance("Present")).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Mark Absent", command=lambda: self.update_attendance("Absent")).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Save Attendance", command=self.save_attendance).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Load Attendance", command=self.load_attendance).grid(row=0, column=3, padx=5)

    def add_student(self):
        roll = self.roll_entry.get().strip()
        name = self.name_entry.get().strip()
        if not roll or not name:
            messagebox.showwarning("Input Error", "Please enter both roll number and name.")
            return
        try:
            self.system.add_student(roll, name)
            self.refresh_table()
            self.roll_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in self.system.students:
            self.tree.insert("", tk.END, values=(s.roll_no, s.name, s.attendance))

    def update_attendance(self, status):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a student.")
            return
        roll_no = self.tree.item(selected)["values"][0]
        self.system.mark_attendance(roll_no, status)
        self.refresh_table()

    def save_attendance(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV Files", "*.csv")])
        if filename:
            self.system.save_to_csv(filename)
            messagebox.showinfo("Success", "Attendance saved successfully!")

    def load_attendance(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename:
            try:
                self.system.load_from_csv(filename)
                self.refresh_table()
                messagebox.showinfo("Success", "Attendance loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = AttendanceApp(root)
#     root.geometry("700x500")
#     root.mainloop()
