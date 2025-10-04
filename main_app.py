"""
Desktop App Chấm Công với Nhận Diện Khuôn Mặt
Main Application - GUI sử dụng Tkinter + OpenCV
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import cv2
from PIL import Image, ImageTk
from datetime import datetime
import threading
import os

from database import EmployeeDatabase, AttendanceLog
from face_recognition_module import FaceRecognizer
from greeting_system import GreetingSystem

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Chấm Công Nhận Diện Khuôn Mặt")
        self.root.geometry("1200x700")
        
        # Initialize components
        self.db = EmployeeDatabase()
        self.attendance_log = AttendanceLog()
        self.face_recognizer = FaceRecognizer(tolerance=0.5)
        self.greeting_system = GreetingSystem()
        
        # Load known faces
        self.face_recognizer.load_known_faces(self.db.get_all_employees())
        
        # Camera
        self.camera = None
        self.camera_running = False
        self.current_frame = None
        
        # Tracking attendance
        self.last_recognized = {}  # {employee_id: timestamp}
        self.recognition_cooldown = 30  # seconds (tránh ghi log liên tục)
        
        # Setup GUI
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Left panel - Camera feed
        left_panel = ttk.LabelFrame(main_container, text="Camera Trực Tiếp", padding="10")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.camera_label = ttk.Label(left_panel)
        self.camera_label.pack()
        
        # Camera controls
        camera_controls = ttk.Frame(left_panel)
        camera_controls.pack(pady=10)
        
        self.start_camera_btn = ttk.Button(
            camera_controls, 
            text="🎥 Bật Camera", 
            command=self.start_camera
        )
        self.start_camera_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_camera_btn = ttk.Button(
            camera_controls, 
            text="⏹ Tắt Camera", 
            command=self.stop_camera,
            state=tk.DISABLED
        )
        self.stop_camera_btn.pack(side=tk.LEFT, padx=5)
        
        # Right panel - Info and controls
        right_panel = ttk.Frame(main_container, padding="10")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Employee info section
        info_frame = ttk.LabelFrame(right_panel, text="Thông Tin Nhân Viên", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.info_text = tk.Text(info_frame, height=10, width=40, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Today's attendance
        attendance_frame = ttk.LabelFrame(right_panel, text="Chấm Công Hôm Nay", padding="10")
        attendance_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar for attendance list
        scroll = ttk.Scrollbar(attendance_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.attendance_listbox = tk.Listbox(
            attendance_frame, 
            yscrollcommand=scroll.set,
            height=10
        )
        self.attendance_listbox.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.attendance_listbox.yview)
        
        # Buttons
        button_frame = ttk.Frame(right_panel)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame, 
            text="➕ Thêm Nhân Viên", 
            command=self.add_employee_dialog
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            button_frame, 
            text="📋 Xem Danh Sách NV", 
            command=self.view_employees
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            button_frame, 
            text="📊 Xuất File CSV", 
            command=self.export_attendance
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            button_frame, 
            text="🔄 Làm Mới", 
            command=self.refresh_today_attendance
        ).pack(fill=tk.X, pady=2)
        
        # Status bar
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = ttk.Label(
            main_container, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN
        )
        status_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Load today's attendance
        self.refresh_today_attendance()
    
    def start_camera(self):
        """Bật camera"""
        if not self.camera_running:
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                self.camera_running = True
                self.start_camera_btn.config(state=tk.DISABLED)
                self.stop_camera_btn.config(state=tk.NORMAL)
                self.status_var.set("Camera đang chạy...")
                self.update_camera_feed()
            else:
                messagebox.showerror("Lỗi", "Không thể mở camera!")
    
    def stop_camera(self):
        """Tắt camera"""
        self.camera_running = False
        if self.camera:
            self.camera.release()
        self.start_camera_btn.config(state=tk.NORMAL)
        self.stop_camera_btn.config(state=tk.DISABLED)
        self.status_var.set("Camera đã tắt")
        self.camera_label.config(image='')
    
    def update_camera_feed(self):
        """Cập nhật video feed từ camera"""
        if self.camera_running and self.camera:
            ret, frame = self.camera.read()
            if ret:
                self.current_frame = frame.copy()
                
                # Nhận diện khuôn mặt
                face_results = self.face_recognizer.detect_and_recognize(frame)
                
                # Xử lý từng khuôn mặt
                for face_info in face_results:
                    employee_id = face_info['employee_id']
                    
                    if employee_id:
                        employee = self.db.get_employee(employee_id)
                        name = employee['name']
                        
                        # Vẽ bounding box
                        frame = self.face_recognizer.draw_face_box(frame, face_info, name)
                        
                        # Kiểm tra và ghi log chấm công
                        self.process_attendance(employee_id, name)
                    else:
                        # Khuôn mặt lạ
                        frame = self.face_recognizer.draw_face_box(frame, face_info, "Unknown")
                
                # Chuyển đổi frame để hiển thị trong Tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (640, 480))
                img = Image.fromarray(frame_resized)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.camera_label.imgtk = imgtk
                self.camera_label.config(image=imgtk)
            
            # Lặp lại sau 10ms
            self.root.after(10, self.update_camera_feed)
    
    def process_attendance(self, employee_id, name):
        """Xử lý chấm công cho nhân viên"""
        now = datetime.now()
        
        # Kiểm tra cooldown
        if employee_id in self.last_recognized:
            time_diff = (now - self.last_recognized[employee_id]).total_seconds()
            if time_diff < self.recognition_cooldown:
                return
        
        # Ghi log chấm công
        timestamp = self.attendance_log.log_attendance(employee_id, name)
        self.last_recognized[employee_id] = now
        
        # Chào nhân viên
        self.greeting_system.greet_employee(name, employee_id)
        
        # Cập nhật UI
        self.update_employee_info(employee_id, name, timestamp)
        self.refresh_today_attendance()
        
        self.status_var.set(f"✅ {name} đã chấm công lúc {timestamp}")
    
    def update_employee_info(self, employee_id, name, timestamp):
        """Cập nhật thông tin nhân viên lên UI"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info = f"""
╔══════════════════════════════╗
║   CHẤM CÔNG THÀNH CÔNG!      ║
╚══════════════════════════════╝

👤 Tên: {name}
🆔 ID: {employee_id}
⏰ Thời gian: {timestamp}

✅ Chúc bạn một ngày làm việc vui vẻ!
        """
        
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
    
    def refresh_today_attendance(self):
        """Làm mới danh sách chấm công hôm nay"""
        self.attendance_listbox.delete(0, tk.END)
        
        today_records = self.attendance_log.get_today_attendance()
        for record in today_records:
            display_text = f"{record['Thời gian']} - {record['Tên']} ({record['Loại']})"
            self.attendance_listbox.insert(tk.END, display_text)
    
    def add_employee_dialog(self):
        """Dialog thêm nhân viên mới"""
        if not self.camera_running:
            messagebox.showwarning("Cảnh báo", "Vui lòng bật camera trước!")
            return
        
        # Nhập thông tin
        employee_id = simpledialog.askstring("Thêm Nhân Viên", "Nhập ID nhân viên:")
        if not employee_id:
            return
        
        # Kiểm tra ID đã tồn tại
        if self.db.get_employee(employee_id):
            messagebox.showerror("Lỗi", "ID nhân viên đã tồn tại!")
            return
        
        name = simpledialog.askstring("Thêm Nhân Viên", "Nhập tên nhân viên:")
        if not name:
            return
        
        # Chụp ảnh và tạo encoding
        if self.current_frame is not None:
            face_encoding = self.face_recognizer.create_face_encoding(self.current_frame)
            
            if face_encoding is not None:
                # Lưu vào database
                self.db.add_employee(employee_id, name, face_encoding)
                
                # Reload known faces
                self.face_recognizer.load_known_faces(self.db.get_all_employees())
                
                messagebox.showinfo("Thành công", f"Đã thêm nhân viên {name}!")
                self.status_var.set(f"Đã thêm nhân viên: {name}")
            else:
                messagebox.showerror("Lỗi", "Không phát hiện khuôn mặt! Vui lòng thử lại.")
    
    def view_employees(self):
        """Xem danh sách nhân viên"""
        employees = self.db.get_all_employees()
        
        # Tạo cửa sổ mới
        view_window = tk.Toplevel(self.root)
        view_window.title("Danh Sách Nhân Viên")
        view_window.geometry("500x400")
        
        # Treeview
        tree_frame = ttk.Frame(view_window, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Tên', 'Ngày tạo'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Tên', text='Tên')
        tree.heading('Ngày tạo', text='Ngày tạo')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Thêm dữ liệu
        for emp_id, emp_data in employees.items():
            tree.insert('', tk.END, values=(emp_id, emp_data['name'], emp_data['created_at']))
        
        # Button xóa
        def delete_selected():
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                emp_id = item['values'][0]
                
                if messagebox.askyesno("Xác nhận", f"Xóa nhân viên {item['values'][1]}?"):
                    self.db.delete_employee(emp_id)
                    self.face_recognizer.load_known_faces(self.db.get_all_employees())
                    tree.delete(selected[0])
                    messagebox.showinfo("Thành công", "Đã xóa nhân viên!")
        
        ttk.Button(view_window, text="🗑 Xóa nhân viên đã chọn", command=delete_selected).pack(pady=10)
    
    def export_attendance(self):
        """Xuất file CSV chấm công"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"attendance_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        
        if filename:
            output_file = self.attendance_log.export_to_csv(filename)
            if output_file:
                messagebox.showinfo("Thành công", f"Đã xuất file: {output_file}")
                self.status_var.set(f"Đã xuất CSV: {output_file}")
    
    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        if self.camera_running:
            self.stop_camera()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = AttendanceApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
