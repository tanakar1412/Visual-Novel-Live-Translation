# Live Translator for Japanese Visual Novels

This tool allows you to capture text from a selected region of your screen, extract Japanese text using Tesseract OCR, and translate it into English in real time using Google Translate.

## 🚀 Features
- Real-time text recognition and translation
- Works best with static (non-animated) text in games
- Adjustable capture region
- Automatic text filtering to improve translation accuracy

## 🔧 Installation

### 1. Install Dependencies
Ensure you have Python installed (>=3.7), then install the required libraries:
```bash
pip install opencv-python numpy pytesseract pillow deep-translator
```

### 2. Install Tesseract OCR
- Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- Set the path in the script:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
  ```

## 📝 Usage
1. Run the script:
   ```bash
   python live_translator.py
   ```
2. Click **"Select Region"** and drag over the text area.
3. Ensure the message box has **high opacity**; otherwise, the program may not read the text correctly.
4. Works best with **non-animated** text in games or visual novels.
5. Translations update automatically as new text appears.

## ⚠️ Known Issues & Tips
- **Does not work well with moving or animated text.**
- **If translation accuracy is low**, try increasing text contrast in the game settings.
- **Reduce background transparency** of the text box for better recognition.

## 📜 License
This project is open-source and available under the MIT License.
