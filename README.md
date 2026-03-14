# ResumeIQ — AI-Powered Resume Analyzer

🔗 **Live Demo:** https://ai-resume-analyzer-production-768b.up.railway.app  
🐙 **GitHub:** https://github.com/roshan-kamath/AI-Resume-Analyzer

---

## What It Does

- 📄 Upload your resume as a PDF
- 📋 Paste any job description
- 📊 Get an instant match score (TF-IDF cosine similarity)
- 🧠 See exactly which skills you have vs what's missing (spaCy NER)
- ✍️ One click — AI rewrites your resume bullets with stronger verbs, metrics, and keywords tailored to that specific role

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

Get a free key at [console.groq.com](https://console.groq.com) — no credit card needed.

```python
# In app.py line 20:
ai_client = Groq(api_key="your_groq_key_here")
```

**5. Run**
```bash
python app.py
```

Open `http://127.0.0.1:5000`

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

## Lessons Learned

First time working with NLP and spaCy. It took me a while to understand why semantic similarity beats a hardcoded keyword list — but once it clicked, the difference was obvious. Also learned the hard way that browser file references break between two fetch calls, which is why the rewrite endpoint uses the already-saved file instead of re-uploading.

Went from zero deployment experience to a live Railway app with env variables and auto-deploy on push. Broke things multiple times. Fixed all of them.

---

## Author

**Roshan Kamath**  
- GitHub: [@roshan-kamath](https://github.com/roshan-kamath)  
- LinkedIn: www.linkedin.com/in/roshan-kamath-9806b337b
