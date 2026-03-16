"""ARIA — Multi-Tenant Schemas

Client types: candidate, company
Each client gets a UUID-based ID (cand_xxx / comp_xxx).
Registry tracks all active clients.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

CLIENTS_DIR = Path(__file__).parent.resolve() / "clients"
REGISTRY_PATH = CLIENTS_DIR / "registry.json"


# ---------------------------------------------------------------------------
# ID generation
# ---------------------------------------------------------------------------

def new_candidate_id() -> str:
    return f"cand_{uuid.uuid4().hex[:12]}"


def new_company_id() -> str:
    return f"comp_{uuid.uuid4().hex[:12]}"


def new_job_id() -> str:
    return f"job_{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def load_registry() -> list[dict]:
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text())
    return []


def save_registry(entries: list[dict]):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(entries, indent=2))


def register_client(client_id: str, client_type: str, name: str) -> dict:
    entries = load_registry()
    entry = {
        "id": client_id,
        "type": client_type,
        "name": name,
        "created": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat(),
    }
    entries.append(entry)
    save_registry(entries)
    return entry


def touch_client(client_id: str):
    """Update last_active timestamp."""
    entries = load_registry()
    for e in entries:
        if e["id"] == client_id:
            e["last_active"] = datetime.now().isoformat()
            break
    save_registry(entries)


def find_client(client_id: str) -> dict | None:
    for e in load_registry():
        if e["id"] == client_id:
            return e
    return None


def list_clients(client_type: str | None = None) -> list[dict]:
    entries = load_registry()
    if client_type:
        return [e for e in entries if e["type"] == client_type]
    return entries


# ---------------------------------------------------------------------------
# Client directory helpers
# ---------------------------------------------------------------------------

def client_dir(client_id: str) -> Path:
    if client_id.startswith("cand_"):
        return CLIENTS_DIR / "candidates" / client_id
    elif client_id.startswith("comp_"):
        return CLIENTS_DIR / "companies" / client_id
    raise ValueError(f"Unknown client ID format: {client_id}")


def detect_client_type(client_id: str) -> str:
    if client_id.startswith("cand_"):
        return "candidate"
    elif client_id.startswith("comp_"):
        return "company"
    raise ValueError(f"Unknown client ID format: {client_id}")


# ---------------------------------------------------------------------------
# Candidate profile
# ---------------------------------------------------------------------------

CANDIDATE_SCHEMA = {
    "id": {"type": str, "required": True},
    "name": {"type": str, "required": True},
    "email": {"type": str, "required": True},
    "phone": {"type": str, "required": False},
    "location": {"type": str, "required": True},
    "linkedin_url": {"type": str, "required": False},
    "github_url": {"type": str, "required": False},
    "portfolio_url": {"type": str, "required": False},
    "years_experience": {"type": int, "required": True},
    "current_role": {"type": str, "required": True},
    "target_roles": {"type": list, "required": True},
    "target_companies": {"type": list, "required": False},
    "skills": {"type": list, "required": True},
    "resume_text": {"type": str, "required": False},
    "achievements": {"type": list, "required": False},
    "education": {"type": list, "required": False},
    "certifications": {"type": list, "required": False},
    "uvp": {"type": str, "required": False},
    "brand_statement": {"type": str, "required": False},
}


def create_candidate_profile(client_id: str, name: str, email: str) -> dict:
    profile = {}
    for key, spec in CANDIDATE_SCHEMA.items():
        if spec["type"] == str:
            profile[key] = ""
        elif spec["type"] == int:
            profile[key] = 0
        elif spec["type"] == list:
            profile[key] = []
    profile["id"] = client_id
    profile["name"] = name
    profile["email"] = email
    return profile


# ---------------------------------------------------------------------------
# Company profile
# ---------------------------------------------------------------------------

COMPANY_SCHEMA = {
    "id": {"type": str, "required": True},
    "name": {"type": str, "required": True},
    "industry": {"type": str, "required": True},
    "size": {"type": str, "required": False},
    "location": {"type": str, "required": False},
    "website": {"type": str, "required": False},
    "culture_values": {"type": list, "required": False},
    "tech_stack": {"type": list, "required": False},
    "benefits": {"type": list, "required": False},
    "description": {"type": str, "required": False},
}


def create_company_profile(client_id: str, name: str, industry: str) -> dict:
    profile = {}
    for key, spec in COMPANY_SCHEMA.items():
        if spec["type"] == str:
            profile[key] = ""
        elif spec["type"] == int:
            profile[key] = 0
        elif spec["type"] == list:
            profile[key] = []
    profile["id"] = client_id
    profile["name"] = name
    profile["industry"] = industry
    return profile


# ---------------------------------------------------------------------------
# Job description schema
# ---------------------------------------------------------------------------

JOB_SCHEMA = {
    "id": {"type": str, "required": True},
    "company_id": {"type": str, "required": True},
    "title": {"type": str, "required": True},
    "department": {"type": str, "required": False},
    "location": {"type": str, "required": False},
    "remote": {"type": bool, "required": False},
    "salary_range": {"type": str, "required": False},
    "description": {"type": str, "required": False},
    "requirements": {"type": list, "required": False},
    "nice_to_have": {"type": list, "required": False},
    "created": {"type": str, "required": False},
}


def create_job(company_id: str, title: str) -> dict:
    job_id = new_job_id()
    return {
        "id": job_id,
        "company_id": company_id,
        "title": title,
        "department": "",
        "location": "",
        "remote": False,
        "salary_range": "",
        "description": "",
        "requirements": [],
        "nice_to_have": [],
        "created": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_profile(profile: dict, schema: dict | None = None) -> list[str]:
    if schema is None:
        if profile.get("id", "").startswith("comp_"):
            schema = COMPANY_SCHEMA
        else:
            schema = CANDIDATE_SCHEMA
    errors = []
    for key, spec in schema.items():
        if spec["required"] and (key not in profile or not profile[key]):
            errors.append(f"Missing required field: {key}")
    return errors


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def save_profile(profile: dict) -> Path:
    cid = profile["id"]
    cdir = client_dir(cid)
    cdir.mkdir(parents=True, exist_ok=True)
    path = cdir / "profile.json"
    path.write_text(json.dumps(profile, indent=2))
    return path


def load_profile(client_id: str) -> dict | None:
    path = client_dir(client_id) / "profile.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


def save_job(job: dict) -> Path:
    cdir = client_dir(job["company_id"]) / "jobs"
    cdir.mkdir(parents=True, exist_ok=True)
    path = cdir / f"{job['id']}.json"
    path.write_text(json.dumps(job, indent=2))
    return path


def load_job(company_id: str, job_id: str) -> dict | None:
    path = client_dir(company_id) / "jobs" / f"{job_id}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


def list_jobs(company_id: str) -> list[dict]:
    jobs_dir = client_dir(company_id) / "jobs"
    if not jobs_dir.exists():
        return []
    jobs = []
    for p in jobs_dir.glob("job_*.json"):
        jobs.append(json.loads(p.read_text()))
    return jobs


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_CANDIDATE = {
    "id": "",  # filled at creation
    "name": "Test User",
    "email": "test@example.com",
    "phone": "",
    "location": "New York, NY",
    "linkedin_url": "https://linkedin.com/in/testuser",
    "github_url": "https://github.com/testuser",
    "portfolio_url": "",
    "years_experience": 6,
    "current_role": "Senior Software Engineer",
    "target_roles": ["Staff Engineer", "Engineering Manager"],
    "target_companies": ["Google", "Stripe", "Vercel"],
    "skills": [
        "Python", "JavaScript", "TypeScript", "React", "Node.js",
        "AWS", "Docker", "Kubernetes", "PostgreSQL", "Redis",
        "System Design", "CI/CD", "GraphQL", "REST APIs",
        "Team Leadership", "Mentoring", "Agile/Scrum"
    ],
    "resume_text": "",
    "achievements": [
        "Built real-time analytics dashboard processing 500K events/day",
        "Led migration from monolith to microservices — 70% faster deploys",
        "Reduced cloud spend by 35% through container optimization",
        "Mentored 4 junior engineers, 2 promoted within a year",
    ],
    "education": ["B.S. Computer Science, NYU"],
    "certifications": ["AWS Solutions Architect Associate"],
    "uvp": "",
    "brand_statement": "",
}

SAMPLE_COMPANY = {
    "id": "",  # filled at creation
    "name": "Acme Corp",
    "industry": "Tech",
    "size": "500-1000",
    "location": "San Francisco, CA",
    "website": "https://acme.example.com",
    "culture_values": ["Innovation", "Collaboration", "Transparency"],
    "tech_stack": ["Python", "React", "AWS", "PostgreSQL", "Kubernetes"],
    "benefits": ["Remote-first", "Unlimited PTO", "Equity"],
    "description": "Acme Corp builds developer tools for the modern stack.",
}
