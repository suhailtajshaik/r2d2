#!/usr/bin/env python3
"""ARIA — Portfolio Site Generator (Multi-Tenant)

Generates a self-contained HTML portfolio site for a candidate.
Single HTML file with Tailwind CDN — no build step, instant deploy.
Includes JSON-LD Person schema, llms.txt hidden div, dark/light toggle, mobile-first.
"""

import json
import html as html_lib
import sys
from pathlib import Path


def escape(text: str) -> str:
    """HTML-escape text."""
    return html_lib.escape(str(text)) if text else ""


def generate_portfolio(profile: dict, output_dir: Path | None = None) -> Path:
    """Generate a static portfolio HTML file for a candidate."""
    name = profile.get("name", "Candidate")

    if output_dir is None:
        from schema import client_dir
        cid = profile.get("id", "")
        if cid:
            output_dir = client_dir(cid) / "portfolio"
        else:
            output_dir = Path(__file__).parent / "output" / name.lower().replace(" ", "_") / "portfolio"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build data
    email = profile.get("email", "")
    location = profile.get("location", "")
    current_role = profile.get("current_role", "")
    uvp = profile.get("uvp", "") or profile.get("brand_statement", "") or f"{current_role} with {profile.get('years_experience', 0)}+ years of experience"
    brand_statement = profile.get("brand_statement", "") or uvp
    linkedin = profile.get("linkedin_url", "")
    github = profile.get("github_url", "")
    skills = profile.get("skills", [])
    achievements = profile.get("achievements", [])
    years_exp = profile.get("years_experience", 0)
    target_roles = profile.get("target_roles", [])
    education = profile.get("education", [])
    certifications = profile.get("certifications", [])

    skill_groups = _categorize_skills(skills)

    # JSON-LD Person schema
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "jobTitle": current_role,
        "description": brand_statement,
        "email": f"mailto:{email}" if email else "",
        "address": {"@type": "PostalAddress", "addressLocality": location} if location else {},
        "knowsAbout": skills,
        "sameAs": [u for u in [linkedin, github] if u],
    }

    # llms.txt content
    llms_txt = f"""# {name}
> {brand_statement}

## Role
{current_role} | {location} | {years_exp} years experience

## Skills
{', '.join(skills)}

## Achievements
{chr(10).join(f'- {a}' for a in achievements)}

## Contact
Email: {email}
LinkedIn: {linkedin}
GitHub: {github}
"""

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(name)} — {escape(current_role)}</title>
    <meta name="description" content="{escape(brand_statement)}">
    <meta name="author" content="{escape(name)}">
    <meta property="og:title" content="{escape(name)} — {escape(current_role)}">
    <meta property="og:description" content="{escape(brand_statement)}">
    <meta property="og:type" content="profile">

    <!-- JSON-LD Person Schema -->
    <script type="application/ld+json">
    {json.dumps(json_ld, indent=2)}
    </script>

    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        primary: '#2563eb',
                        accent: '#7c3aed',
                    }}
                }}
            }}
        }}
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .gradient-text {{
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .card-hover {{ transition: transform 0.2s, box-shadow 0.2s; }}
        .card-hover:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
    </style>
</head>
<body class="bg-gray-50 text-gray-800 dark:bg-gray-900 dark:text-gray-100 transition-colors duration-300">

    <!-- Dark/Light Toggle -->
    <button id="theme-toggle" class="fixed top-4 right-4 z-50 p-2 rounded-full bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 hover:scale-110 transition" aria-label="Toggle dark mode">
        <svg id="sun-icon" class="w-5 h-5 hidden dark:block text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"/></svg>
        <svg id="moon-icon" class="w-5 h-5 block dark:hidden text-gray-700" fill="currentColor" viewBox="0 0 20 20"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/></svg>
    </button>

    <!-- Hero Section -->
    <header class="bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700">
        <div class="max-w-4xl mx-auto px-6 py-16 md:py-24 text-center">
            <h1 class="text-4xl md:text-5xl font-bold mb-4 gradient-text">{escape(name)}</h1>
            <p class="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-3">{escape(current_role)}</p>
            <p class="text-lg text-gray-500 dark:text-gray-400 mb-8 max-w-2xl mx-auto">{escape(uvp)}</p>
            <div class="flex flex-wrap justify-center gap-4">
                {f'<a href="mailto:{escape(email)}" class="bg-primary text-white px-6 py-3 rounded-lg font-medium hover:opacity-90 transition">Get in Touch</a>' if email else ''}
                {f'<a href="{escape(linkedin)}" target="_blank" rel="noopener" class="border border-gray-300 dark:border-gray-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition">LinkedIn</a>' if linkedin else ''}
                {f'<a href="{escape(github)}" target="_blank" rel="noopener" class="border border-gray-300 dark:border-gray-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition">GitHub</a>' if github else ''}
            </div>
        </div>
    </header>

    <!-- About Section -->
    <section class="max-w-4xl mx-auto px-6 py-16">
        <h2 class="text-2xl font-bold mb-6">About</h2>
        <div class="grid md:grid-cols-3 gap-6">
            <div class="card-hover bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
                <div class="text-3xl font-bold text-primary mb-2">{years_exp}+</div>
                <div class="text-gray-500 dark:text-gray-400">Years Experience</div>
            </div>
            <div class="card-hover bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
                <div class="text-3xl font-bold text-primary mb-2">{len(skills)}</div>
                <div class="text-gray-500 dark:text-gray-400">Technical Skills</div>
            </div>
            <div class="card-hover bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
                <div class="text-3xl font-bold text-primary mb-2">{len(achievements)}</div>
                <div class="text-gray-500 dark:text-gray-400">Key Achievements</div>
            </div>
        </div>
        {f'<div class="mt-8"><p class="text-gray-600 dark:text-gray-300 leading-relaxed">{escape(brand_statement)}</p>{f"""<p class="text-gray-500 dark:text-gray-400 mt-2">{escape(location)}</p>""" if location else ""}</div>' if brand_statement != uvp else ''}
    </section>

    <!-- Skills Section -->
    <section class="bg-white dark:bg-gray-800 border-y border-gray-100 dark:border-gray-700">
        <div class="max-w-4xl mx-auto px-6 py-16">
            <h2 class="text-2xl font-bold mb-8">Skills & Expertise</h2>
            {_render_skill_groups(skill_groups)}
        </div>
    </section>

    <!-- Achievements Section -->
    {f"""<section class="max-w-4xl mx-auto px-6 py-16">
        <h2 class="text-2xl font-bold mb-8">Key Achievements</h2>
        <div class="space-y-4">
            {''.join(f'<div class="card-hover bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border-l-4 border-primary"><p class="text-gray-700 dark:text-gray-300">{escape(a)}</p></div>' for a in achievements)}
        </div>
    </section>""" if achievements else ''}

    <!-- Education & Certifications -->
    {_render_education_section(education, certifications)}

    <!-- Contact Section -->
    <section class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h2 class="text-2xl font-bold mb-4">Let's Connect</h2>
        <p class="text-gray-500 dark:text-gray-400 mb-8 max-w-lg mx-auto">
            {f"Interested in {', '.join(escape(r) for r in target_roles[:2])} roles. " if target_roles else ''}
            Open to opportunities and collaborations.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
            {f'<a href="mailto:{escape(email)}" class="bg-primary text-white px-8 py-3 rounded-lg font-medium hover:opacity-90 transition">{escape(email)}</a>' if email else ''}
            {f'<a href="{escape(linkedin)}" target="_blank" rel="noopener" class="border border-gray-300 dark:border-gray-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition">LinkedIn</a>' if linkedin else ''}
            {f'<a href="{escape(github)}" target="_blank" rel="noopener" class="border border-gray-300 dark:border-gray-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition">GitHub</a>' if github else ''}
        </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-gray-100 dark:border-gray-700 py-8 text-center text-gray-400 text-sm">
        <p>&copy; 2026 {escape(name)}. Built with ARIA.</p>
    </footer>

    <!-- Hidden llms.txt for AI crawlers -->
    <div id="llms-txt" style="display:none" aria-hidden="true">
{escape(llms_txt)}
    </div>

    <!-- Dark mode script -->
    <script>
        const toggle = document.getElementById('theme-toggle');
        const html = document.documentElement;
        if (localStorage.theme === 'dark' || (!localStorage.theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
            html.classList.add('dark');
        }}
        toggle.addEventListener('click', () => {{
            html.classList.toggle('dark');
            localStorage.theme = html.classList.contains('dark') ? 'dark' : 'light';
        }});
    </script>

</body>
</html>"""

    output_path = output_dir / "index.html"
    output_path.write_text(html_content)

    # Also write llms.txt
    llms_path = output_dir / "llms.txt"
    llms_path.write_text(llms_txt)

    print(f"  Portfolio: {output_path}")
    print(f"  llms.txt: {llms_path}")
    return output_path


def _render_education_section(education: list, certifications: list) -> str:
    if not education and not certifications:
        return ''
    edu_html = ''
    if education:
        items = ''.join(f'<p class="text-gray-600 dark:text-gray-300 mb-2">{escape(e)}</p>' for e in education)
        edu_html = f'<div><h3 class="font-semibold text-lg mb-3">Education</h3>{items}</div>'
    cert_html = ''
    if certifications:
        items = ''.join(f'<p class="text-gray-600 dark:text-gray-300 mb-2">{escape(c)}</p>' for c in certifications)
        cert_html = f'<div><h3 class="font-semibold text-lg mb-3">Certifications</h3>{items}</div>'
    return f"""<section class="bg-white dark:bg-gray-800 border-y border-gray-100 dark:border-gray-700">
        <div class="max-w-4xl mx-auto px-6 py-16">
            <h2 class="text-2xl font-bold mb-8">Education &amp; Certifications</h2>
            <div class="grid md:grid-cols-2 gap-6">
                {edu_html}
                {cert_html}
            </div>
        </div>
    </section>"""


def _categorize_skills(skills: list) -> dict:
    categories = {
        "Languages": {"python", "javascript", "typescript", "java", "go", "rust",
                       "ruby", "php", "c++", "c#", "scala", "kotlin", "swift", "r"},
        "Frontend": {"react", "angular", "vue", "next.js", "nextjs", "tailwind",
                      "bootstrap", "css", "html", "sass", "webpack", "vite"},
        "Backend": {"node.js", "nodejs", "django", "flask", "fastapi", "express",
                     "spring", "graphql", "rest apis", "grpc"},
        "Cloud & DevOps": {"aws", "gcp", "azure", "docker", "kubernetes", "terraform",
                           "ci/cd", "jenkins", "github actions", "vercel", "netlify"},
        "Data & Databases": {"postgresql", "mysql", "mongodb", "redis", "kafka",
                              "elasticsearch", "spark", "airflow", "snowflake", "bigquery"},
        "Leadership": {"team leadership", "mentoring", "agile/scrum", "project management",
                        "system design", "architecture"},
    }
    grouped = {}
    used = set()
    for cat, keywords in categories.items():
        matches = [s for s in skills if s.lower() in keywords]
        if matches:
            grouped[cat] = matches
            used.update(matches)
    remaining = [s for s in skills if s not in used]
    if remaining:
        grouped["Other"] = remaining
    return grouped


def _render_skill_groups(groups: dict) -> str:
    if not groups:
        return '<p class="text-gray-500">No skills listed.</p>'
    parts = ['<div class="grid md:grid-cols-2 gap-6">']
    for category, skills in groups.items():
        pills = ''.join(
            f'<span class="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-3 py-1 rounded-full text-sm font-medium">{escape(s)}</span>'
            for s in skills
        )
        parts.append(f'<div class="card-hover bg-gray-50 dark:bg-gray-700/50 rounded-xl p-6"><h3 class="font-semibold text-gray-700 dark:text-gray-200 mb-3">{escape(category)}</h3><div class="flex flex-wrap gap-2">{pills}</div></div>')
    parts.append('</div>')
    return '\n'.join(parts)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python portfolio_generator.py <profile.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        profile = json.load(f)
    generate_portfolio(profile)
