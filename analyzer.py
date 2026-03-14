import pdfplumber
import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy model — run once: python -m spacy download en_core_web_md
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_md"])
    nlp = spacy.load("en_core_web_md")

# Broad skills taxonomy — reference anchors for semantic matching
SKILLS_TAXONOMY = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "bash",
    # Web
    "react", "vue", "angular", "next.js", "node.js", "express", "fastapi",
    "django", "flask", "html", "css", "tailwind", "graphql", "rest api",
    # Data & ML
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
    "pytorch", "keras", "scikit-learn", "pandas", "numpy", "data analysis",
    "data visualization", "statistics", "a/b testing", "feature engineering",
    "llm", "fine-tuning", "rag", "vector database", "hugging face",
    # Databases
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "sqlite", "dynamodb", "cassandra", "firebase",
    # Cloud & DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ci/cd",
    "jenkins", "github actions", "linux", "nginx", "microservices", "serverless",
    # Tools & Practices
    "git", "agile", "scrum", "jira", "figma", "postman",
    "unit testing", "tdd", "system design", "api design",
]


def extract_text(pdf_file):
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print("PDF Error:", e)
        return ""
    return text.lower()


def extract_resume_bullets(pdf_file):
    """Extract bullet-point style experience lines from the resume."""
    bullets = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if not page_text:
                    continue
                for line in page_text.split("\n"):
                    line = line.strip()
                    # Keep lines that look like experience/achievement statements
                    if len(line) > 40 and any(c.isalpha() for c in line):
                        skip_headers = r'^(education|experience|skills|projects|contact|summary|objective|references|phone|email|linkedin|github|http)'
                        if not re.match(skip_headers, line.lower()):
                            bullets.append(line)
    except Exception as e:
        print("Bullet extraction error:", e)
    # Return up to 8 best candidates
    return bullets[:8]


def extract_skills_spacy(text):
    """
    Use spaCy NER + noun chunks + taxonomy matching
    to extract skills far beyond a simple keyword list.
    """
    doc = nlp(text[:100000])  # guard against huge inputs
    candidates = set()

    # 1. Named entities — PRODUCT/ORG often surface tech tool names
    for ent in doc.ents:
        if ent.label_ in ("PRODUCT", "ORG", "WORK_OF_ART"):
            candidates.add(ent.text.lower().strip())

    # 2. Noun chunks — multi-word technical phrases
    for chunk in doc.noun_chunks:
        cleaned = chunk.text.lower().strip()
        words = cleaned.split()
        if 1 <= len(words) <= 3 and len(cleaned) > 2:
            candidates.add(cleaned)

    # 3. Individual technical tokens
    for token in doc:
        if token.pos_ in ("PROPN", "NOUN") and not token.is_stop and len(token.text) > 2:
            candidates.add(token.text.lower().strip())

    # 4. Match candidates to taxonomy via substring + spaCy semantic similarity
    matched_skills = []
    for skill in SKILLS_TAXONOMY:
        # Fast path: direct substring
        if skill in text:
            matched_skills.append(skill)
            continue
        # Semantic path: vector similarity
        skill_doc = nlp(skill)
        if skill_doc.has_vector:
            for candidate in candidates:
                cand_doc = nlp(candidate)
                if cand_doc.has_vector and skill_doc.similarity(cand_doc) > 0.82:
                    matched_skills.append(skill)
                    break

    return list(set(matched_skills))


def calculate_similarity(resume, job_desc):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume, job_desc])
    score = cosine_similarity(vectors[0:1], vectors[1:2])
    return round(score[0][0] * 100, 2)


def missing_skills(resume_skills, job_skills):
    return [s for s in job_skills if s not in resume_skills]


def generate_verdict(score, found, missing):
    score = float(score)
    found_count = len(found)
    missing_count = len(missing)

    if score >= 75:
        title = "Strong Match"
        verdict = (
            f"Your resume aligns well with this role — {found_count} key skills detected. "
            "You're a competitive candidate; targeted additions could push you to the top."
        )
        rec_parts = [
            f"Strong foundation with {found_count} matching skills including {', '.join(found[:3]) if found else 'several key areas'}. Quantify your achievements — numbers and impact statements dramatically increase callback rates.",
        ]
        if missing:
            rec_parts.append(f"Consider adding {', '.join(missing[:3])} if you have exposure, even through side projects.")
        rec_parts.append("Mirror the exact language from the job description in your summary — ATS systems reward keyword alignment.")

    elif score >= 50:
        title = "Good Potential"
        verdict = (
            f"Solid foundation with {found_count} matching skills, but {missing_count} gap{'s' if missing_count != 1 else ''} could hurt your ranking. "
            "Bridging those gaps would significantly boost your competitiveness."
        )
        rec_parts = [
            f"Your matched skills ({', '.join(found[:4]) if found else 'the ones listed'}) are relevant but need more prominence — move them higher and add measurable context.",
        ]
        if missing:
            rec_parts.append(f"Biggest gaps to address: {', '.join(missing[:5])}. Even beginner-level exposure helps pass ATS filters.")
        rec_parts.append("Rewrite your experience bullets to mirror the job description's phrasing. Recruiters spend ~7 seconds on first scan.")

    else:
        title = "Needs Work"
        verdict = (
            f"Significant mismatch — only {found_count} skills align. "
            "Your resume needs a targeted overhaul before submitting."
        )
        rec_parts = [
            "As-is, this resume is unlikely to pass ATS screening for this role. Rewrite your skills section with exact keywords from the job posting.",
        ]
        if missing:
            rec_parts.append(f"Priority skills to add or develop: {', '.join(missing[:6])}. A short course or project justifies listing them.")
        rec_parts.append("Use this analysis as a concrete upskilling roadmap for the next 2-3 months.")
        if found:
            rec_parts.append(f"Build on your existing strengths — {', '.join(found[:2])} are solid foundations. Link them to measurable outcomes.")

    return title, verdict, "\n\n".join(rec_parts)