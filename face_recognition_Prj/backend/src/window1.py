import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import pyttsx3
import pandas as pd
from datetime import datetime

# Initialize speech engine
# engine = pyttsx3.init()

# Global DataFrame to simulate attendance records
attendance_df = pd.DataFrame(columns=["EmpID", "Name", "Department", "Date", "Status"])

# ----------------------- MAIN APP WINDOW -----------------------
root = tk.Tk()
root.title("Attendance Management System")
# root.geometry("420x280")
root.state('zoomed') 
root.config(bg="#f0f0f0")

frame = tk.Frame(root, bg="#ffffff", bd=5, relief=tk.RIDGE)
frame.pack(fill=tk.BOTH, expand=True)
# frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=350, height=220)

# ----------------------- STYLE BUTTONS -----------------------
style = ttk.Style()
style.theme_use('clam')  # Use a basic theme

# Create a 3D button style with rounded edges (using padding, borderwidth)
style.configure("Rounded.TButton",
                font=("Segoe UI", 12, "bold"),
                padding=10,
                relief="raised",          # Raised to simulate 3D
                borderwidth=3,
                background="#4CAF50",
                foreground="white")

# Define active color when the button is pressed
style.map("Rounded.TButton",
          background=[('active', '#45a049')],
          relief=[('pressed', 'sunken')])

# ----------------------- ENROLLMENT WINDOW -----------------------
def open_enrollment():
    enroll_win = tk.Toplevel(root)
    enroll_win.title("Employee Enrollment")
    enroll_win.geometry("400x400")

    tk.Label(enroll_win, text="Department:").pack(pady=5)
    dept_entry = tk.Entry(enroll_win)
    dept_entry.pack()

    tk.Label(enroll_win, text="Employee ID:").pack(pady=5)
    emp_id_entry = tk.Entry(enroll_win)
    emp_id_entry.pack()

    tk.Label(enroll_win, text="Name:").pack(pady=5)
    name_entry = tk.Entry(enroll_win)
    name_entry.pack()

    img_label = tk.Label(enroll_win)
    img_label.pack(pady=10)

    captured_image = [None]  # mutable reference to hold photo

    def capture_photo():
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("employee_photo.jpg", frame)
            img = Image.open("employee_photo.jpg")
            img = img.resize((150, 150))
            imgtk = ImageTk.PhotoImage(img)
            img_label.config(image=imgtk)
            img_label.image = imgtk
            captured_image[0] = frame
        cap.release()
        cv2.destroyAllWindows()

    def save_record():
        dept = dept_entry.get()
        emp_id = emp_id_entry.get()
        name = name_entry.get()
        if not all([dept, emp_id, name]):
            messagebox.showerror("Error", "All fields are required")
            return

        global attendance_df
        new_record = {"EmpID": emp_id, "Name": name, "Department": dept, "Date": datetime.now().date(), "Status": "Enrolled"}
        attendance_df = pd.concat([attendance_df, pd.DataFrame([new_record])], ignore_index=True)
        # engine.say("Record saved successfully")
        # engine.runAndWait()
        messagebox.showinfo("Saved", "Record saved successfully!")

    ttk.Button(enroll_win, text="Capture Picture", style="3D.TButton", command=capture_photo).pack(pady=5)
    ttk.Button(enroll_win, text="Save", style="3D.TButton", command=save_record).pack(pady=10)

# ----------------------- START SCANNER -----------------------
def start_scanner():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # press q to quit
            break
    cap.release()
    cv2.destroyAllWindows()

# ----------------------- ATTENDANCE REPORT -----------------------
def open_report_window():
    report_win = tk.Toplevel(root)
    report_win.title("Attendance Reports")
    report_win.geometry("350x250")

    def open_emp_search():
        search_win = tk.Toplevel(report_win)
        search_win.title("Search by Employee ID")
        search_win.geometry("400x300")

        tk.Label(search_win, text="Enter Employee ID:").pack(pady=5)
        emp_id_entry = tk.Entry(search_win)
        emp_id_entry.pack()

        tree = ttk.Treeview(search_win, columns=("Date", "Status"), show='headings')
        tree.heading("Date", text="Date")
        tree.heading("Status", text="Status")
        tree.pack(fill='both', expand=True)

        def search():
            emp_id = emp_id_entry.get()
            data = attendance_df[attendance_df["EmpID"] == emp_id]
            for i in tree.get_children():
                tree.delete(i)
            for _, row in data.iterrows():
                tree.insert("", tk.END, values=(row["Date"], row["Status"]))

        def export_excel():
            emp_id = emp_id_entry.get()
            data = attendance_df[attendance_df["EmpID"] == emp_id]
            if data.empty:
                messagebox.showerror("Error", "No data to export")
                return
            filename = f"{emp_id}_attendance.xlsx"
            data.to_excel(filename, index=False)
            messagebox.showinfo("Exported", f"Exported to {filename}")

        ttk.Button(search_win, text="Search", style="3D.TButton", command=search).pack(pady=5)
        ttk.Button(search_win, text="Export to Excel", style="3D.TButton", command=export_excel).pack(pady=5)

    def open_between_dates():
        date_win = tk.Toplevel(report_win)
        date_win.title("Attendance Between Dates")
        date_win.geometry("400x350")

        tk.Label(date_win, text="Start Date (YYYY-MM-DD):").pack(pady=5)
        start_entry = tk.Entry(date_win)
        start_entry.pack()

        tk.Label(date_win, text="End Date (YYYY-MM-DD):").pack(pady=5)
        end_entry = tk.Entry(date_win)
        end_entry.pack()

        tree = ttk.Treeview(date_win, columns=("EmpID", "Name", "Date", "Status"), show='headings')
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill='both', expand=True)

        def filter_dates():
            start = start_entry.get()
            end = end_entry.get()
            try:
                mask = (pd.to_datetime(attendance_df["Date"]) >= pd.to_datetime(start)) & \
                       (pd.to_datetime(attendance_df["Date"]) <= pd.to_datetime(end))
                data = attendance_df[mask]
                for i in tree.get_children():
                    tree.delete(i)
                for _, row in data.iterrows():
                    tree.insert("", tk.END, values=(row["EmpID"], row["Name"], row["Date"], row["Status"]))
            except Exception:
                messagebox.showerror("Error", "Invalid date format")

        def export_excel():
            start = start_entry.get()
            end = end_entry.get()
            mask = (pd.to_datetime(attendance_df["Date"]) >= pd.to_datetime(start)) & \
                   (pd.to_datetime(attendance_df["Date"]) <= pd.to_datetime(end))
            data = attendance_df[mask]
            if data.empty:
                messagebox.showerror("Error", "No data to export")
                return
            filename = f"attendance_{start}_to_{end}.xlsx"
            data.to_excel(filename, index=False)
            messagebox.showinfo("Exported", f"Exported to {filename}")

        ttk.Button(date_win, text="Search", style="3D.TButton", command=filter_dates).pack(pady=5)
        ttk.Button(date_win, text="Export to Excel", style="3D.TButton", command=export_excel).pack(pady=5)

    ttk.Button(report_win, text="Search by Employee ID", style="3D.TButton", command=open_emp_search).pack(pady=10, fill='x')
    ttk.Button(report_win, text="Attendance Between Dates", style="3D.TButton", command=open_between_dates).pack(pady=10, fill='x')

# ----------------------- MAIN BUTTONS -----------------------
ttk.Button(frame, text="Enrollment", style="3D.TButton", command=open_enrollment).grid(row=0, column=0, padx=10, pady=8, sticky="ew")
ttk.Button(frame, text="Start Scanner", style="3D.TButton", command=start_scanner).grid(row=0, column=1, padx=10, pady=8, sticky="ew")
ttk.Button(frame, text="Attendance Report", style="3D.TButton", command=open_report_window).grid(row=0, column=2, padx=10, pady=8, sticky="ew")

# Set column weight to make them expand equally
frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=1)
frame.grid_columnconfigure(2, weight=1)

frame.grid_rowconfigure(0, weight=1)

root.mainloop()
