import time
import threading
import pytesseract
import cv2
import numpy as np
import tkinter as tk
from deep_translator import GoogleTranslator
from PIL import ImageGrab, Image
import re  

# Path to Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Globals
capture_region = None
selection_window = None
is_translating = False
start_x = start_y = end_x = end_y = 0
last_extracted_text = ""
translation_thread = None

def select_region():
    global selection_window, canvas, start_x, start_y, end_x, end_y

    if selection_window:
        return

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
    global capture_region, selection_window, is_translating, translation_thread

    end_x, end_y = event.x, event.y
    selection_window.destroy()
    selection_window = None

    if start_x == end_x or start_y == end_y:
        translation_label.config(text="Invalid selection! Try again.")
        return

    capture_region = (min(start_x, end_x), min(start_y, end_y), max(start_x, end_x), max(start_y, end_y))

    if not is_translating:
        is_translating = True
        translation_thread = threading.Thread(target=auto_translate, daemon=True)
        translation_thread.start()

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return binary

def filter_japanese(text):
    return "".join(re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]+', text))

def auto_translate():
    global is_translating
    while is_translating:
        capture_and_translate()
        time.sleep(0.5)

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

        if extracted_text and extracted_text != last_extracted_text:
            translated_text = GoogleTranslator(source='ja', target='en').translate(extracted_text)
            translation_label.config(text=translated_text)
            last_extracted_text = extracted_text

    except Exception as e:
        print(f"[ERROR] {e}")
        translation_label.config(text="An error occurred. Check console.")

# GUI setup
root = tk.Tk()
root.title("Live Translator")
root.geometry("500x250")
root.configure(bg="black")
root.attributes("-topmost", True)
root.attributes("-alpha", 0.8)

select_button = tk.Button(root, text="Select Region", command=select_region)
select_button.pack(pady=10)

translation_label = tk.Label(root, text="Click 'Select Region' to start", fg="white", bg="black",
                             font=("Arial", 16, "bold"), wraplength=480, justify="left")
translation_label.pack(expand=True, fill="both")

root.mainloop()
