from PIL import Image
import pytesseract

# Path to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load test image
img = Image.open("test_note.jpg")

# OCR with Sinhala + English
text = pytesseract.image_to_string(img, lang="sin+eng")

print("===== Extracted Text =====")
print(text)
