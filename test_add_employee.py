"""
Script test để xem modal thêm nhân viên
Chạy script này để test giao diện mà không cần mở camera
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import cv2
import numpy as np

def create_test_frame():
    """Tạo một frame giả để test"""
    # Tạo một hình ảnh test màu xanh dương
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (200, 150, 100)  # BGR color
    
    # Vẽ text lên frame
    cv2.putText(frame, "TEST IMAGE", (200, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    return frame

def show_add_employee_dialog(root, current_frame):
    """Dialog thêm nhân viên mới với form đầy đủ"""
    
    # Tạo dialog window
    dialog = tk.Toplevel(root)
    dialog.title("➕ Thêm Nhân Viên Mới")
    dialog.geometry("450x500")
    dialog.resizable(False, False)
    dialog.grab_set()  # Modal dialog
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
    y = (dialog.winfo_screenheight() // 2) - (500 // 2)
    dialog.geometry(f"450x500+{x}+{y}")
    
    # Main frame
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(
        main_frame, 
        text="📝 THÔNG TIN NHÂN VIÊN MỚI",
        font=('Arial', 14, 'bold')
    )
    title_label.pack(pady=(0, 20))
    
    # Camera preview frame
    preview_frame = ttk.LabelFrame(main_frame, text="📸 Hình ảnh từ camera", padding="10")
    preview_frame.pack(fill=tk.X, pady=(0, 15))
    
    preview_label = ttk.Label(preview_frame)
    preview_label.pack()
    
    # Show current camera frame
    if current_frame is not None:
        frame_resized = cv2.resize(current_frame, (300, 225))
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        preview_label.imgtk = imgtk
        preview_label.config(image=imgtk)
    
    # Form fields
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    
    # ID field
    ttk.Label(form_frame, text="🆔 Mã nhân viên:", font=('Arial', 10)).grid(
        row=0, column=0, sticky=tk.W, pady=8
    )
    id_entry = ttk.Entry(form_frame, width=30, font=('Arial', 10))
    id_entry.grid(row=0, column=1, pady=8, padx=(10, 0))
    id_entry.focus()
    
    # Name field
    ttk.Label(form_frame, text="👤 Họ và tên:", font=('Arial', 10)).grid(
        row=1, column=0, sticky=tk.W, pady=8
    )
    name_entry = ttk.Entry(form_frame, width=30, font=('Arial', 10))
    name_entry.grid(row=1, column=1, pady=8, padx=(10, 0))
    
    # Birth date field
    ttk.Label(form_frame, text="🎂 Ngày sinh:", font=('Arial', 10)).grid(
        row=2, column=0, sticky=tk.W, pady=8
    )
    
    # Birth date frame with 3 comboboxes
    birth_frame = ttk.Frame(form_frame)
    birth_frame.grid(row=2, column=1, pady=8, padx=(10, 0), sticky=tk.W)
    
    # Day
    day_var = tk.StringVar()
    day_combo = ttk.Combobox(
        birth_frame, 
        textvariable=day_var, 
        width=5,
        values=[f"{i:02d}" for i in range(1, 32)],
        state='readonly'
    )
    day_combo.set("01")
    day_combo.pack(side=tk.LEFT, padx=2)
    
    ttk.Label(birth_frame, text="/").pack(side=tk.LEFT)
    
    # Month
    month_var = tk.StringVar()
    month_combo = ttk.Combobox(
        birth_frame,
        textvariable=month_var,
        width=5,
        values=[f"{i:02d}" for i in range(1, 13)],
        state='readonly'
    )
    month_combo.set("01")
    month_combo.pack(side=tk.LEFT, padx=2)
    
    ttk.Label(birth_frame, text="/").pack(side=tk.LEFT)
    
    # Year
    year_var = tk.StringVar()
    current_year = datetime.now().year
    year_combo = ttk.Combobox(
        birth_frame,
        textvariable=year_var,
        width=8,
        values=[str(y) for y in range(current_year - 70, current_year - 15)],
        state='readonly'
    )
    year_combo.set(str(current_year - 25))
    year_combo.pack(side=tk.LEFT, padx=2)
    
    # Error label
    error_label = ttk.Label(form_frame, text="", foreground="red", font=('Arial', 9))
    error_label.grid(row=3, column=0, columnspan=2, pady=5)
    
    # Buttons frame
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X)
    
    def save_employee():
        """Lưu thông tin nhân viên"""
        employee_id = id_entry.get().strip()
        name = name_entry.get().strip()
        birth_date = f"{day_var.get()}/{month_var.get()}/{year_var.get()}"
        
        # Validation
        if not employee_id:
            error_label.config(text="⚠️ Vui lòng nhập mã nhân viên!")
            id_entry.focus()
            return
        
        if not name:
            error_label.config(text="⚠️ Vui lòng nhập họ tên!")
            name_entry.focus()
            return
        
        # Success
        dialog.destroy()
        messagebox.showinfo(
            "Thành công", 
            f"✅ Đã thêm nhân viên:\n\n👤 {name}\n🆔 {employee_id}\n🎂 {birth_date}"
        )
    
    def cancel():
        """Hủy bỏ"""
        dialog.destroy()
    
    # Save button
    save_btn = ttk.Button(
        button_frame,
        text="✅ Lưu thông tin",
        command=save_employee
    )
    save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
    
    # Cancel button
    cancel_btn = ttk.Button(
        button_frame,
        text="❌ Hủy bỏ",
        command=cancel
    )
    cancel_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
    
    # Bind Enter key to save
    dialog.bind('<Return>', lambda e: save_employee())
    dialog.bind('<Escape>', lambda e: cancel())


def main():
    """Main function"""
    root = tk.Tk()
    root.title("Test Modal Thêm Nhân Viên")
    root.geometry("400x200")
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (400 // 2)
    y = (root.winfo_screenheight() // 2) - (200 // 2)
    root.geometry(f"400x200+{x}+{y}")
    
    frame = ttk.Frame(root, padding="40")
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(
        frame, 
        text="Test Giao Diện Thêm Nhân Viên",
        font=('Arial', 12, 'bold')
    ).pack(pady=20)
    
    test_frame = create_test_frame()
    
    ttk.Button(
        frame,
        text="➕ Mở Modal Thêm Nhân Viên",
        command=lambda: show_add_employee_dialog(root, test_frame),
        width=30
    ).pack()
    
    root.mainloop()


if __name__ == "__main__":
    main()
