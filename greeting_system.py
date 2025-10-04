"""
Hệ thống chào hỏi nhân viên bằng text-to-speech
Hỗ trợ giọng nữ Tiếng Việt
"""
import pyttsx3
import threading
from datetime import datetime
import os
import tempfile

# Import gTTS cho giọng Việt tốt hơn (optional)
try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

class GreetingSystem:
    def __init__(self, use_gtts=True):
        """
        use_gtts: True = dùng Google TTS (giọng Việt tự nhiên, cần internet)
                  False = dùng pyttsx3 (offline, giọng robot hơn)
        """
        self.use_gtts = use_gtts and GTTS_AVAILABLE
        self.greeted_today = set()  # Tránh chào lặp lại trong cùng 1 ngày
        
        if not self.use_gtts:
            self.engine = pyttsx3.init()
            self.setup_voice()
        else:
            # Khởi tạo pygame mixer cho phát âm thanh
            try:
                pygame.mixer.init()
            except:
                # Fallback về pyttsx3 nếu pygame không hoạt động
                self.use_gtts = False
                self.engine = pyttsx3.init()
                self.setup_voice()
    
    def setup_voice(self):
        """Cấu hình giọng nói cho pyttsx3 (offline)"""
        # Tốc độ nói (words per minute)
        self.engine.setProperty('rate', 150)
        
        # Âm lượng (0.0 to 1.0)
        self.engine.setProperty('volume', 0.9)
        
        # Tìm giọng nữ
        voices = self.engine.getProperty('voices')
        
        # In ra danh sách giọng để debug
        print("=== Danh sách giọng có sẵn ===")
        for idx, voice in enumerate(voices):
            print(f"{idx}: {voice.name} - {voice.id}")
            print(f"   Languages: {voice.languages}")
            print(f"   Gender: {getattr(voice, 'gender', 'unknown')}")
        
        # Thử tìm giọng nữ Tiếng Việt hoặc giọng nữ
        female_voice = None
        for voice in voices:
            voice_name_lower = voice.name.lower()
            
            # Ưu tiên giọng Việt Nam nữ
            if 'vietnam' in voice_name_lower and 'female' in voice_name_lower:
                female_voice = voice.id
                print(f"\n✅ Đã chọn giọng: {voice.name}")
                break
            
            # Thử tìm giọng nữ tiếng Anh (Zira, Hazel, Susan, etc.)
            if any(name in voice_name_lower for name in ['zira', 'hazel', 'susan', 'female']):
                female_voice = voice.id
        
        if female_voice:
            self.engine.setProperty('voice', female_voice)
            print(f"✅ Đã đặt giọng nữ")
        else:
            print("⚠️ Không tìm thấy giọng nữ, dùng giọng mặc định")
    
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
            if self.use_gtts:
                # Dùng Google TTS - giọng nữ Việt Nam tự nhiên
                self._speak_gtts(message)
            else:
                # Dùng pyttsx3 - offline
                self.engine.say(message)
                self.engine.runAndWait()
        except Exception as e:
            print(f"Lỗi TTS: {e}")
    
    def _speak_gtts(self, message):
        """Phát âm bằng Google TTS (giọng nữ Việt Nam)"""
        try:
            # Tạo file âm thanh tạm
            tts = gTTS(text=message, lang='vi', slow=False)
            
            # Lưu vào file tạm
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_filename = temp_file.name
            temp_file.close()
            
            tts.save(temp_filename)
            
            # Phát âm thanh
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            # Đợi phát xong
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Xóa file tạm
            try:
                os.unlink(temp_filename)
            except:
                pass
                
        except Exception as e:
            print(f"Lỗi Google TTS: {e}")
            # Fallback về pyttsx3
            if hasattr(self, 'engine'):
                self.engine.say(message)
                self.engine.runAndWait()
    
    def greet_unknown(self):
        """Chào người lạ"""
        message = "Xin chào! Vui lòng đăng ký thông tin."
        thread = threading.Thread(target=self._speak, args=(message,))
        thread.daemon = True
        thread.start()
    
    def reset_daily_greetings(self):
        """Reset danh sách đã chào (gọi vào đầu ngày mới)"""
        self.greeted_today.clear()
