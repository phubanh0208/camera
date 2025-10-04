"""
Module nhận diện khuôn mặt sử dụng face_recognition library
"""
import cv2
import face_recognition
import numpy as np

class FaceRecognizer:
    def __init__(self, tolerance=0.6):
        """
        tolerance: Ngưỡng để nhận diện (càng nhỏ càng strict)
        0.6 là giá trị mặc định tốt
        """
        self.tolerance = tolerance
        self.known_face_encodings = []
        self.known_face_ids = []
    
    def load_known_faces(self, employees_dict):
        """Load danh sách khuôn mặt đã biết từ database"""
        self.known_face_encodings = []
        self.known_face_ids = []
        
        for emp_id, emp_data in employees_dict.items():
            self.known_face_encodings.append(emp_data['face_encoding'])
            self.known_face_ids.append(emp_id)
    
    def detect_and_recognize(self, frame):
        """
        Phát hiện và nhận diện khuôn mặt trong frame
        Returns: List of tuples (face_location, employee_id, name)
        """
        # Resize frame để tăng tốc độ xử lý
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Tìm tất cả khuôn mặt và encoding trong frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        results = []
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # So sánh với các khuôn mặt đã biết
            matches = face_recognition.compare_faces(
                self.known_face_encodings, 
                face_encoding, 
                tolerance=self.tolerance
            )
            
            employee_id = None
            name = "Unknown"
            
            if True in matches:
                # Tìm khuôn mặt khớp nhất
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, 
                    face_encoding
                )
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    employee_id = self.known_face_ids[best_match_index]
            
            # Scale lại vị trí về kích thước ban đầu
            top, right, bottom, left = face_location
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            results.append({
                'location': (top, right, bottom, left),
                'employee_id': employee_id,
                'encoding': face_encoding
            })
        
        return results
    
    def create_face_encoding(self, image):
        """
        Tạo encoding từ ảnh khuôn mặt
        Returns: face_encoding hoặc None nếu không tìm thấy khuôn mặt
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_image)
        
        if len(face_encodings) > 0:
            return face_encodings[0]
        return None
    
    def draw_face_box(self, frame, face_info, employee_name=None):
        """Vẽ bounding box và tên lên frame"""
        top, right, bottom, left = face_info['location']
        
        # Chọn màu: xanh lá nếu nhận diện được, đỏ nếu không
        color = (0, 255, 0) if face_info['employee_id'] else (0, 0, 255)
        
        # Vẽ khung chữ nhật
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Vẽ khung tên
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        
        # Hiển thị tên
        font = cv2.FONT_HERSHEY_DUPLEX
        name_text = employee_name if employee_name else "Unknown"
        cv2.putText(frame, name_text, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
        
        return frame
