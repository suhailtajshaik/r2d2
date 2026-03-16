#!/usr/bin/env python3
"""ARIA — ATS Keyword Analyzer

Analyzes job descriptions against resumes to calculate ATS match scores
and provide keyword optimization recommendations.
"""

import re
import sys
from collections import Counter


# Common filler words to exclude from keyword extraction
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "need",
    "must", "it", "its", "you", "your", "we", "our", "they", "their",
    "this", "that", "these", "those", "i", "me", "my", "he", "she",
    "him", "her", "his", "them", "who", "which", "what", "where", "when",
    "how", "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "no", "not", "only", "own", "same", "so", "than",
    "too", "very", "just", "about", "above", "after", "again", "also",
    "any", "because", "before", "between", "during", "into", "through",
    "under", "until", "up", "out", "over", "then", "once", "here",
    "there", "why", "well", "etc", "work", "working", "experience",
    "role", "team", "ability", "including", "using", "across", "within",
    "strong", "required", "preferred", "plus", "years", "year",
    "responsibilities", "requirements", "qualifications", "job",
    "position", "company", "opportunity", "looking", "join",
}

# Patterns that indicate important multi-word technical terms
TECH_PATTERNS = [
    r"machine\s+learning", r"deep\s+learning", r"natural\s+language\s+processing",
    r"computer\s+vision", r"data\s+engineer(?:ing)?", r"data\s+scien(?:ce|tist)",
    r"full[\s-]?stack", r"front[\s-]?end", r"back[\s-]?end",
    r"ci[\s/]cd", r"dev[\s]?ops", r"site\s+reliability",
    r"cloud\s+computing", r"micro[\s-]?services", r"event[\s-]?driven",
    r"rest(?:ful)?\s+api", r"graph[\s]?ql", r"web\s+services",
    r"unit\s+test(?:ing)?", r"test[\s-]?driven", r"agile[\s/]scrum",
    r"cross[\s-]?functional", r"project\s+management",
    r"system\s+design", r"distributed\s+systems",
    r"amazon\s+web\s+services", r"google\s+cloud",
    r"version\s+control", r"object[\s-]?oriented",
]


def normalize(text: str) -> str:
    """Normalize text for comparison."""
    return re.sub(r'[^a-z0-9+#.\s]', ' ', text.lower()).strip()


def extract_keywords(text: str) -> dict:
    """Extract meaningful keywords and phrases from text.

    Returns dict with:
    - single_keywords: set of individual important words
    - phrases: set of multi-word technical terms found
    - skills: set of likely technical skills (capitalized terms, acronyms)
    """
    normalized = normalize(text)

    # Extract multi-word technical terms first
    phrases = set()
    for pattern in TECH_PATTERNS:
        matches = re.findall(pattern, normalized)
        phrases.update(m.strip() for m in matches)

    # Extract single keywords (excluding stop words)
    words = normalized.split()
    keywords = set()
    for word in words:
        if len(word) > 2 and word not in STOP_WORDS:
            keywords.add(word)

    # Extract likely technical terms from original text (capitalized, acronyms)
    skills = set()
    # Acronyms: AWS, CI/CD, SQL, etc.
    acronyms = re.findall(r'\b[A-Z][A-Z0-9+#]{1,10}\b', text)
    skills.update(a.lower() for a in acronyms)

    # CamelCase or capitalized tech terms
    tech_terms = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', text)
    skills.update(t.lower() for t in tech_terms)

    # Common tech tools/frameworks (look for capitalized single words in context)
    tool_pattern = re.findall(
        r'\b(Python|Java|JavaScript|TypeScript|React|Angular|Vue|Node\.?js|'
        r'Docker|Kubernetes|Terraform|AWS|GCP|Azure|PostgreSQL|MySQL|MongoDB|'
        r'Redis|Kafka|RabbitMQ|Elasticsearch|GraphQL|REST|gRPC|'
        r'Git|Jenkins|GitHub|GitLab|CircleCI|Datadog|Splunk|'
        r'Spark|Hadoop|Airflow|dbt|Snowflake|BigQuery|'
        r'Linux|Nginx|Apache|Vercel|Netlify|Heroku|'
        r'TensorFlow|PyTorch|Pandas|NumPy|Scikit-learn|'
        r'Swift|Kotlin|Rust|Go|Ruby|PHP|C\+\+|C#|Scala|'
        r'Spring|Django|Flask|FastAPI|Express|Next\.?js|'
        r'Tailwind|Bootstrap|SASS|LESS|Webpack|Vite)\b',
        text, re.IGNORECASE
    )
    skills.update(t.lower() for t in tool_pattern)

    return {
        "single_keywords": keywords,
        "phrases": phrases,
        "skills": skills,
    }


def analyze_match(job_description: str, resume_text: str) -> dict:
    """Analyze keyword match between a job description and resume.

    Returns:
        dict with present_keywords, missing_keywords, match_score, recommendations
    """
    jd_data = extract_keywords(job_description)
    resume_data = extract_keywords(resume_text)

    resume_normalized = normalize(resume_text)

    # Check skills match
    jd_skills = jd_data["skills"]
    present_skills = set()
    missing_skills = set()
    for skill in jd_skills:
        if skill in resume_normalized or skill.replace(".", "") in resume_normalized:
            present_skills.add(skill)
        else:
            missing_skills.add(skill)

    # Check phrase match
    present_phrases = set()
    missing_phrases = set()
    for phrase in jd_data["phrases"]:
        if phrase in resume_normalized:
            present_phrases.add(phrase)
        else:
            missing_phrases.add(phrase)

    # Check important keyword overlap (top keywords by frequency in JD)
    jd_words = [w for w in normalize(job_description).split()
                if len(w) > 2 and w not in STOP_WORDS]
    jd_freq = Counter(jd_words)
    top_keywords = {word for word, count in jd_freq.most_common(30)}

    present_keywords = top_keywords & resume_data["single_keywords"]
    missing_keywords = top_keywords - resume_data["single_keywords"]

    # Combine all
    all_present = present_skills | present_phrases | present_keywords
    all_missing = missing_skills | missing_phrases | missing_keywords
    total = len(all_present) + len(all_missing)
    match_score = round((len(all_present) / total * 100) if total > 0 else 0, 1)

    # Generate recommendations
    recommendations = []
    if missing_skills:
        recommendations.append(
            f"Add these technical skills if you have them: {', '.join(sorted(missing_skills))}"
        )
    if missing_phrases:
        recommendations.append(
            f"Include these key phrases: {', '.join(sorted(missing_phrases))}"
        )
    if match_score < 60:
        recommendations.append(
            "Your match score is below 60% — significant tailoring needed. "
            "Consider rewriting your summary and experience sections with JD keywords."
        )
    elif match_score < 80:
        recommendations.append(
            "Good foundation but needs keyword optimization. "
            "Weave missing keywords naturally into your experience bullets."
        )
    else:
        recommendations.append(
            "Strong keyword match! Focus on quantifying achievements and "
            "ensuring your experience bullets mirror the JD's language exactly."
        )

    if len(resume_text.split()) < 300:
        recommendations.append(
            "Resume seems short. Ensure all relevant experience and skills are included."
        )

    return {
        "present_keywords": sorted(all_present),
        "missing_keywords": sorted(all_missing),
        "match_score": match_score,
        "skill_match": {
            "present": sorted(present_skills),
            "missing": sorted(missing_skills),
        },
        "phrase_match": {
            "present": sorted(present_phrases),
            "missing": sorted(missing_phrases),
        },
        "recommendations": recommendations,
    }


def print_report(result: dict):
    """Print a formatted ATS analysis report."""
    print("\n" + "=" * 60)
    print("📊 ATS KEYWORD ANALYSIS REPORT")
    print("=" * 60)

    score = result["match_score"]
    if score >= 80:
        grade = "🟢 STRONG"
    elif score >= 60:
        grade = "🟡 MODERATE"
    else:
        grade = "🔴 WEAK"

    print(f"\n  Match Score: {score}% {grade}")

    print(f"\n  ✅ Present Keywords ({len(result['present_keywords'])}):")
    for kw in result["present_keywords"]:
        print(f"     • {kw}")

    print(f"\n  ❌ Missing Keywords ({len(result['missing_keywords'])}):")
    for kw in result["missing_keywords"]:
        print(f"     • {kw}")

    if result["skill_match"]["missing"]:
        print(f"\n  🔧 Missing Technical Skills:")
        for s in result["skill_match"]["missing"]:
            print(f"     • {s}")

    print(f"\n  💡 Recommendations:")
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"     {i}. {rec}")

    print("\n" + "=" * 60)


def main():
    """CLI entry point for standalone ATS analysis."""
    if len(sys.argv) < 3:
        print("""
📊 ARIA ATS Keyword Analyzer

Usage:
  python ats_analyzer.py <job_description_file> <resume_file>

Example:
  python ats_analyzer.py jd.txt resume.txt
""")
        return

    jd_path = sys.argv[1]
    resume_path = sys.argv[2]

    with open(jd_path) as f:
        jd_text = f.read()
    with open(resume_path) as f:
        resume_text = f.read()

    result = analyze_match(jd_text, resume_text)
    print_report(result)

    # Also save JSON
    import json
    print(f"\n📋 JSON Output:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
