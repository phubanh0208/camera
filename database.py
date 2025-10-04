"""
Database module để quản lý thông tin nhân viên và embedding khuôn mặt
"""
import pickle
import os
from datetime import datetime
import csv

class EmployeeDatabase:
    def __init__(self, db_file='employees.pkl'):
        self.db_file = db_file
        self.employees = self.load_database()
    
    def load_database(self):
        """Load database từ file pickle"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'rb') as f:
                return pickle.load(f)
        return {}
    
    def save_database(self):
        """Lưu database vào file pickle"""
        with open(self.db_file, 'wb') as f:
            pickle.dump(self.employees, f)
    
    def add_employee(self, employee_id, name, face_encoding):
        """Thêm nhân viên mới vào database"""
        self.employees[employee_id] = {
            'name': name,
            'face_encoding': face_encoding,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_database()
        return True
    
    def get_employee(self, employee_id):
        """Lấy thông tin nhân viên theo ID"""
        return self.employees.get(employee_id)
    
    def get_all_employees(self):
        """Lấy danh sách tất cả nhân viên"""
        return self.employees
    
    def delete_employee(self, employee_id):
        """Xóa nhân viên khỏi database"""
        if employee_id in self.employees:
            del self.employees[employee_id]
            self.save_database()
            return True
        return False


class AttendanceLog:
    def __init__(self, log_file='attendance_log.csv'):
        self.log_file = log_file
        self._init_log_file()
    
    def _init_log_file(self):
        """Khởi tạo file log nếu chưa tồn tại"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Thời gian', 'ID nhân viên', 'Tên', 'Loại'])
    
    def log_attendance(self, employee_id, name, attendance_type='check-in'):
        """Ghi log chấm công"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, employee_id, name, attendance_type])
        return timestamp
    
    def get_today_attendance(self):
        """Lấy danh sách chấm công hôm nay"""
        today = datetime.now().strftime('%Y-%m-%d')
        attendance = []
        
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Thời gian'].startswith(today):
                        attendance.append(row)
        return attendance
    
    def export_to_csv(self, output_file=None):
        """Xuất log ra file CSV khác (để backup hoặc gửi HR)"""
        if output_file is None:
            output_file = f'attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as src:
                with open(output_file, 'w', newline='', encoding='utf-8') as dst:
                    dst.write(src.read())
            return output_file
        return None
