from flask import Flask, render_template, request, jsonify
import os
from groq import Groq
from analyzer import (
    extract_text,
    extract_resume_bullets,
    extract_skills_spacy,
    calculate_similarity,
    missing_skills,
    generate_verdict,
)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Groq client
ai_client = Groq(api_key="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")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        resume_file = request.files.get("resume")
        job_desc = request.form.get("job_desc", "").strip()

        if not resume_file:
            return jsonify({"error": "No resume uploaded"}), 400
        if not job_desc:
            return jsonify({"error": "No job description provided"}), 400

        path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
        resume_file.save(path)

        resume_text = extract_text(path)
        if not resume_text:
            return jsonify({"error": "Could not read resume. Please upload a valid PDF."}), 400

        score = calculate_similarity(resume_text, job_desc.lower())

        # spaCy-powered skill extraction
        resume_skills = extract_skills_spacy(resume_text)
        job_skills = extract_skills_spacy(job_desc.lower())
        missing = missing_skills(resume_skills, job_skills)

        title, verdict, recommendations = generate_verdict(score, resume_skills, missing)

        return jsonify({
            "score": score,
            "found_skills": resume_skills,
            "missing_skills": missing,
            "title": title,
            "verdict": verdict,
            "recommendations": recommendations,
        })

    except Exception as e:
        print("Analyze error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/rewrite", methods=["POST"])
def rewrite():
    """
    Uses already-saved resume file from /analyze + job description,
    returns before/after rewrite suggestions via Groq.
    """
    try:
        filename = request.form.get("filename", "").strip()
        job_desc = request.form.get("job_desc", "").strip()

        if not filename or not job_desc:
            return jsonify({"error": "Missing filename or job description"}), 400

        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        if not os.path.exists(path):
            return jsonify({"error": "Resume file not found. Please re-upload and analyze first."}), 400

        bullets = extract_resume_bullets(path)

        if not bullets:
            return jsonify({"error": "Could not extract bullet points from resume."}), 400

        bullets_text = "\n".join(f"- {b}" for b in bullets)

        prompt = f"""You are an expert resume coach. A candidate is applying for the following role:

JOB DESCRIPTION:
{job_desc[:2000]}

Here are their current resume bullet points:
{bullets_text}

For each bullet point, rewrite it to be stronger, more impactful, and better aligned with the job description. Follow these rules:
- Start each bullet with a strong action verb
- Add quantifiable metrics where they could plausibly exist (use realistic estimates like "~20%", "3x faster", etc.)
- Mirror keywords from the job description naturally
- Keep each rewrite concise (1-2 lines max)

Return ONLY a JSON array with this exact structure, no markdown, no explanation:
[
  {{"original": "original bullet text", "rewritten": "improved bullet text", "reason": "one sentence explaining the key improvement"}},
  ...
]"""

        message = ai_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = message.choices[0].message.content.strip()
        # Strip any accidental markdown fences
        raw = raw.replace("```json", "").replace("```", "").strip()

        import json
        rewrites = json.loads(raw)

        return jsonify({"rewrites": rewrites})

    except Exception as e:
        print("Rewrite error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)