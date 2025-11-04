# 📚 StudyPal – Sinhala/English OCR and AI Summarization Tool

**StudyPal** is an AI-powered smart note web application designed to help students quickly extract and summarize study notes from both **Sinhala** and **English** printed or handwritten images.  
It performs **OCR (Optical Character Recognition)** locally using Tesseract and **AI summarization** using an offline Hugging Face transformer model — making it **fast, private, and completely offline** after setup.

---

## 🚀 Features

✅ Upload study note images (Sinhala or English)  
✅ Local OCR using Tesseract (`sin+eng`)  
✅ AI summarization using `facebook/bart-large-cnn` (offline)  
✅ Download summarized content as `.txt` or `.pdf`  
✅ Simple and user-friendly Flask web interface  
✅ Fully offline after initial model download  
✅ Works for printed and moderately clear handwritten notes  

---

## 🧠 Tech Stack

| Component | Technology Used |
|------------|-----------------|
| **Backend** | Flask (Python) |
| **OCR Engine** | Tesseract OCR (Sinhala + English) |
| **Summarization** | Transformers + Torch (facebook/bart-large-cnn) |
| **Frontend** | HTML5, CSS3, Bootstrap |
| **PDF Export** | FPDF |
| **Environment** | Python 3.9+ Virtual Environment |
| **Optional (for testing)** | Hugging Face Inference API (deprecated) |

---

## 📁 Folder Structure

StudyPal/
│
├── app.py # Main Flask application
├── requirements.txt # Python dependencies
├── static/
│ └── uploads/ # Uploaded images
├── summaries/ # Generated summaries (.txt/.pdf)
├── templates/
│ ├── index.html # Upload page
│ └── result.html # Output page
└── README.md # Project documentation

yaml
Copy code
