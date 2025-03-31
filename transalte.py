import time
import threading
import pytesseract
import cv2
import numpy as np
import tkinter as tk
from deep_translator import GoogleTranslator
from PIL import ImageGrab, Image
import re  

# Đường dẫn Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Biến toàn cục
capture_region = None
selection_window = None
is_translating = False  
start_x = start_y = end_x = end_y = 0
last_extracted_text = ""  # Lưu văn bản lần trước

# Hàm chọn vùng OCR
def select_region():
    global selection_window, canvas, start_x, start_y, end_x, end_y

    selection_window = tk.Toplevel(root)
    selection_window.attributes("-fullscreen", True)
    selection_window.attributes("-alpha", 0.3)
    selection_window.config(bg="gray")

    canvas = tk.Canvas(selection_window, bg="gray", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    canvas.bind("<ButtonPress-1>", start_selection)
    canvas.bind("<B1-Motion>", update_selection)
    canvas.bind("<ButtonRelease-1>", end_selection)

def start_selection(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y
    canvas.delete("rect")  

def update_selection(event):
    global end_x, end_y
    end_x, end_y = event.x, event.y
    canvas.delete("rect")
    canvas.create_rectangle(start_x, start_y, end_x, end_y, outline="red", width=2, tags="rect")

def end_selection(event):
    global capture_region, selection_window, is_translating

    end_x, end_y = event.x, event.y

    if start_x == end_x or start_y == end_y:
        translation_label.config(text="Invalid selection! Try again.")
        selection_window.destroy()
        return

    capture_region = (min(start_x, end_x), min(start_y, end_y), max(start_x, end_x), max(start_y, end_y))
    selection_window.destroy()  

    is_translating = True
    threading.Thread(target=auto_translate, daemon=True).start()

# Tối ưu tiền xử lý ảnh
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Chuyển ảnh về grayscale
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)  # Binarization
    return binary

# Lọc chỉ lấy chữ tiếng Nhật
def filter_japanese(text):
    return "".join(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', text))

# Dịch tự động nhanh hơn
def auto_translate():
    global is_translating
    while is_translating:
        capture_and_translate()
        time.sleep(0.5)  # Giảm thời gian chờ xuống còn 0.5 giây

def capture_and_translate():
    global last_extracted_text  

    if not capture_region:
        return

    x1, y1, x2, y2 = capture_region

    try:
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        processed_image = preprocess_image(np.array(screenshot))

        extracted_text = pytesseract.image_to_string(processed_image, lang="jpn", config="--psm 6").strip()
        extracted_text = filter_japanese(extracted_text)  

        # Chỉ dịch nếu văn bản mới khác văn bản cũ
        if extracted_text and extracted_text != last_extracted_text:
            translated_text = GoogleTranslator(source='ja', target='en').translate(extracted_text)
            translation_label.config(text=translated_text)
            last_extracted_text = extracted_text  

    except Exception as e:
        translation_label.config(text=f"Error: {str(e)}")

# GUI
root = tk.Tk()
root.title("Live Translator")
root.geometry("500x250")
root.configure(bg="black")
root.attributes("-topmost", True)
root.attributes("-alpha", 0.8)

select_button = tk.Button(root, text="Select Region", command=select_region)
select_button.pack(pady=10)

translation_label = tk.Label(root, text="Click 'Select Region' to start", fg="white", bg="black", font=("Arial", 16, "bold"))
translation_label.pack(expand=True, fill="both")

root.mainloop()
