# AGENTS.md - Face Recognition Attendance System

## Commands
- **Run app**: `python main_app.py`
- **Install dependencies**: `pip install -r requirements.txt`
- **No tests**: This project currently has no automated tests

## Architecture
- **main_app.py**: Main GUI application using Tkinter + OpenCV, handles camera feed and UI
- **database.py**: Employee database (pickle) and attendance log (CSV) management
- **face_recognition_module.py**: Face detection and recognition using face_recognition library
- **greeting_system.py**: Text-to-speech greetings using pyttsx3
- **Data files**: employees.pkl (employee DB), attendance_log.csv (attendance records)

## Code Style
- **Language**: Python 3, Vietnamese comments and UI text
- **Imports**: Standard library first, then third-party (cv2, face_recognition, pyttsx3), then local modules
- **Classes**: PascalCase (e.g., EmployeeDatabase, FaceRecognizer)
- **Functions/Variables**: snake_case (e.g., load_database, employee_id)
- **Docstrings**: Vietnamese triple-quoted strings for classes and functions
- **Error handling**: Try-except blocks for I/O operations and TTS
- **Threading**: Use daemon threads for non-blocking TTS and camera operations
- **Encoding**: UTF-8 for CSV files with Vietnamese text
