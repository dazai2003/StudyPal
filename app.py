import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import cv2
from fpdf import FPDF
from transformers import pipeline

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "static/uploads"
SUMMARY_FOLDER = "summaries"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SUMMARY_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "replace_this_with_a_random_secret_for_prod"

# ---------------- Helpers ----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    """Basic preprocessing to improve OCR"""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not read image for preprocessing")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, h=30)
    h, w = denoised.shape
    if w < 1000:
        scale = 1000 / w
        denoised = cv2.resize(denoised, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    equ = cv2.equalizeHist(denoised)
    th = cv2.adaptiveThreshold(equ, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 31, 2)
    proc_path = image_path + "_proc.png"
    cv2.imwrite(proc_path, th)
    return proc_path

def run_ocr(image_path):
    """Run Tesseract OCR (Sinhala + English)"""
    text = pytesseract.image_to_string(Image.open(image_path), lang='sin+eng')
    return text

def save_summary_txt(text, base_name):
    path = os.path.join(SUMMARY_FOLDER, f"{base_name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def save_summary_pdf(text, base_name):
    path = os.path.join(SUMMARY_FOLDER, f"{base_name}.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)  # Replace with Sinhala TTF if needed
    pdf.multi_cell(0, 8, text)
    pdf.output(path)
    return path

# ---------------- Offline Summarization ----------------
print("Loading offline summarization model... this may take a few minutes the first time.")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
print("Summarization model loaded.")

def summarize_text(text):
    """Offline summarization"""
    if not text.strip():
        return "No text to summarize."
    # truncate large text
    text = text.strip()[:18000]
    try:
        result = summarizer(text, max_length=200, min_length=50, do_sample=False)
        return result[0]['summary_text']
    except Exception as e:
        print("Local summarization error:", e)
        return "Error during summarization."

# ---------------- Routes ----------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        flash("No image part")
        return redirect(url_for("index"))
    file = request.files["image"]
    if file.filename == "":
        flash("No selected file")
        return redirect(url_for("index"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        try:
            proc_path = preprocess_image(save_path)
        except Exception as e:
            flash(f"Preprocessing failed: {e}")
            return redirect(url_for("index"))

        try:
            extracted_text = run_ocr(proc_path)
        except Exception as e:
            flash(f"OCR failed: {e}")
            extracted_text = ""

        try:
            summary = summarize_text(extracted_text)
        except Exception as e:
            flash(f"Summarization failed: {e}")
            summary = ""

        base_name = os.path.splitext(filename)[0]
        txt_path = save_summary_txt(summary, base_name)
        pdf_path = save_summary_pdf(summary, base_name)

        return render_template("result.html",
                               uploaded_filename=filename,
                               extracted_text=extracted_text,
                               summary=summary,
                               txt_url=url_for("download_file", filename=os.path.basename(txt_path)),
                               pdf_url=url_for("download_file", filename=os.path.basename(pdf_path)))
    else:
        flash("File type not allowed. Only png, jpg, jpeg.")
        return redirect(url_for("index"))

@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    filepath = os.path.join(SUMMARY_FOLDER, filename)
    if not os.path.exists(filepath):
        flash("File not found")
        return redirect(url_for("index"))
    return send_file(filepath, as_attachment=True)

# ---------------- Run Server ----------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
