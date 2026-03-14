# ResumeIQ — AI-Powered Resume Analyzer

A full-stack web app that scores your resume against any job description, detects skill gaps using NLP, and rewrites your resume bullets with AI.

🔗 **Live Demo:** https://ai-resume-analyzer-production-768b.up.railway.app

---

## What It Does

- 📄 Upload your resume as a PDF
- 📋 Paste any job description
- 📊 Get an instant match score powered by TF-IDF cosine similarity
- 🧠 See exactly which skills you have vs what's missing (powered by spaCy NER)
- ✍️ Click one button and watch AI rewrite your resume bullets — stronger action verbs, quantified metrics, tailored to the role

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| NLP / Skill Extraction | spaCy `en_core_web_md` |
| Match Scoring | TF-IDF + Cosine Similarity (scikit-learn) |
| AI Rewrites | Llama 3.3 via Groq API |
| PDF Parsing | pdfplumber |
| Frontend | HTML, CSS, JavaScript |

---

## Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/roshan-kamath/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

**2. Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

**4. Set your Groq API key**

Get a free key at [console.groq.com](https://console.groq.com)

```bash
# In app.py line 20:
ai_client = Groq(api_key="your_groq_key_here")
```

**5. Run the app**
```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

## Project Structure

```
AI-Resume-Analyzer/
├── app.py              # Flask server + API routes
├── analyzer.py         # NLP logic, skill extraction, scoring
├── requirements.txt    # Python dependencies
├── Procfile            # Railway deployment config
└── templates/
    └── index.html      # Frontend (HTML + CSS + JS)
```

---

## How It Works

```
User uploads PDF + job description
        ↓
pdfplumber extracts raw text from PDF
        ↓
spaCy NER identifies skills in resume + job description
        ↓
TF-IDF + cosine similarity calculates match score
        ↓
Results rendered in real time (score ring, skill tags, recommendations)
        ↓
User clicks "Rewrite Bullets"
        ↓
Llama 3.3 via Groq rewrites each bullet with stronger language
        ↓
Before/After cards displayed with one-click copy
```

---

## Author

**Roshan Kamath**
- GitHub: [@roshan-kamath](https://github.com/roshan-kamath)
- LinkedIn: [your linkedin here]