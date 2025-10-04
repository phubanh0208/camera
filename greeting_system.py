"""
Hệ thống chào hỏi nhân viên bằng text-to-speech
"""
import pyttsx3
import threading
from datetime import datetime

class GreetingSystem:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_voice()
        self.greeted_today = set()  # Tránh chào lặp lại trong cùng 1 ngày
    
    def setup_voice(self):
        """Cấu hình giọng nói"""
        # Tốc độ nói (words per minute)
        self.engine.setProperty('rate', 150)
        
        # Âm lượng (0.0 to 1.0)
        self.engine.setProperty('volume', 0.9)
        
        # Chọn giọng (nếu có giọng tiếng Việt)
        voices = self.engine.getProperty('voices')
        # Thử tìm giọng tiếng Việt, nếu không có thì dùng giọng mặc định
        for voice in voices:
            if 'vietnam' in voice.name.lower() or 'vi' in voice.languages:
                self.engine.setProperty('voice', voice.id)
                break
    
    def greet_employee(self, name, employee_id):
        """
        Chào nhân viên
        Chỉ chào 1 lần trong ngày để tránh spam
        """
        today = datetime.now().strftime('%Y-%m-%d')
        greeting_key = f"{employee_id}_{today}"
        
        if greeting_key in self.greeted_today:
            return False
        
        # Tạo lời chào theo thời gian trong ngày
        hour = datetime.now().hour
        if hour < 12:
            time_greeting = "Chào buổi sáng"
        elif hour < 18:
            time_greeting = "Chào buổi chiều"
        else:
            time_greeting = "Chào buổi tối"
        
        message = f"{time_greeting} {name}, chúc một ngày làm việc vui vẻ!"
        
        # Chạy TTS trong thread riêng để không block UI
        thread = threading.Thread(target=self._speak, args=(message,))
        thread.daemon = True
        thread.start()
        
        self.greeted_today.add(greeting_key)
        return True
    
    def _speak(self, message):
        """Phát âm thanh (chạy trong thread riêng)"""
        try:
            self.engine.say(message)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Lỗi TTS: {e}")
    
    def greet_unknown(self):
        """Chào người lạ"""
        message = "Xin chào! Vui lòng đăng ký thông tin."
        thread = threading.Thread(target=self._speak, args=(message,))
        thread.daemon = True
        thread.start()
    
    def reset_daily_greetings(self):
        """Reset danh sách đã chào (gọi vào đầu ngày mới)"""
        self.greeted_today.clear()
