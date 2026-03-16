#!/usr/bin/env python3
"""ARIA — AI Recruitment & Career Intelligence Agent (Multi-Tenant)

One instance serving multiple companies AND candidates simultaneously.
Each client gets a UUID namespace with full data isolation.

Usage:
  # Candidate operations
  python3 aria.py --new-candidate --name "John Doe" --email "john@example.com"
  python3 aria.py --client cand_abc123 --task intake
  python3 aria.py --client cand_abc123 --task resume_analysis
  python3 aria.py --client cand_abc123 --task tailor_resume --job "Senior Engineer at Google"
  python3 aria.py --client cand_abc123 --task linkedin
  python3 aria.py --client cand_abc123 --task brand
  python3 aria.py --client cand_abc123 --task portfolio

  # Company operations
  python3 aria.py --new-company --name "Acme Corp" --industry "Tech"
  python3 aria.py --client comp_xyz789 --task screen_resumes --job job_001
  python3 aria.py --client comp_xyz789 --task write_jd --role "Senior Engineer"
  python3 aria.py --client comp_xyz789 --task weekly_report

  # Batch & admin
  python3 aria.py --batch weekly_checkin
  python3 aria.py --batch portfolio_sync
  python3 aria.py --list-clients
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from schema import (
    CLIENTS_DIR,
    SAMPLE_CANDIDATE,
    SAMPLE_COMPANY,
    client_dir,
    create_candidate_profile,
    create_company_profile,
    create_job,
    detect_client_type,
    find_client,
    list_clients,
    list_jobs,
    load_job,
    load_profile,
    new_candidate_id,
    new_company_id,
    register_client,
    save_job,
    save_profile,
    touch_client,
    validate_profile,
)

AGENT_DIR = Path("/home/r2d2/brain/agents/aria")
PROJECT_DIR = Path(__file__).parent.resolve()

# Load system prompt
SYSTEM_PROMPT = (AGENT_DIR / "ARIA.md").read_text()

CLAUDE_CMD = ["claude", "--permission-mode", "bypassPermissions", "--print"]
CLAUDE_TIMEOUT = 600


# ---------------------------------------------------------------------------
# Claude CLI helpers
# ---------------------------------------------------------------------------

def call_claude(prompt: str, timeout: int = CLAUDE_TIMEOUT) -> str | None:
    """Call Claude CLI and return response text."""
    try:
        result = subprocess.run(
            CLAUDE_CMD + [prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            print(f"[error] Claude CLI error: {result.stderr[:500]}")
            return None
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"[error] Claude CLI timed out after {timeout}s")
        return None
    except FileNotFoundError:
        print("[error] Claude CLI not found. Install: npm install -g @anthropic-ai/claude-code")
        return None


def call_claude_json(prompt: str, timeout: int = CLAUDE_TIMEOUT) -> dict | list | None:
    """Call Claude CLI and parse JSON from response."""
    output = call_claude(prompt, timeout)
    if not output:
        return None
    json_match = re.search(r'[\[{].*[\]}]', output, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return None


# ---------------------------------------------------------------------------
# Session file I/O
# ---------------------------------------------------------------------------

def save_session(client_id: str, session_type: str, content: str, subdir: str = "sessions") -> Path:
    """Save session output to client directory."""
    cdir = client_dir(client_id) / subdir
    cdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = cdir / f"{session_type}_{ts}.md"
    path.write_text(content)
    print(f"  Saved: {path}")
    return path


# ---------------------------------------------------------------------------
# ARIA — Main Agent Class
# ---------------------------------------------------------------------------

class ARIA:
    """Multi-tenant AI Recruitment & Career Intelligence Agent."""

    def __init__(self, client_id: str | None = None):
        self.client_id = client_id
        self.client_type = detect_client_type(client_id) if client_id else None
        self.client_dir = client_dir(client_id) if client_id else None

    def _build_prompt(self, task: str, context: str = "") -> str:
        """Build prompt with system prompt + client context + task."""
        profile = load_profile(self.client_id) if self.client_id else {}
        profile_json = json.dumps(profile, indent=2) if profile else "{}"

        return f"""{SYSTEM_PROMPT}

---

Today's date: {datetime.now().strftime("%Y-%m-%d")}
Client ID: {self.client_id}
Client type: {self.client_type}

## Client Profile
```json
{profile_json}
```

{context}

---

## Task
{task}
"""

    def run_task(self, task: str, **kwargs) -> str | None:
        """Route and execute a task."""
        touch_client(self.client_id)

        dispatch = {
            # Candidate tasks
            "intake": self._task_intake,
            "resume_analysis": self._task_resume_analysis,
            "tailor_resume": self._task_tailor_resume,
            "linkedin": self._task_linkedin,
            "brand": self._task_brand,
            "portfolio": self._task_portfolio,
            # Company tasks
            "screen_resumes": self._task_screen_resumes,
            "write_jd": self._task_write_jd,
            "weekly_report": self._task_weekly_report,
        }

        handler = dispatch.get(task)
        if not handler:
            print(f"[error] Unknown task: {task}")
            print(f"  Available: {', '.join(dispatch.keys())}")
            return None

        print(f"\n>> ARIA | client={self.client_id} | task={task}")
        print("=" * 60)
        result = handler(**kwargs)
        if result:
            print("=" * 60)
            print(f">> Task complete: {task}")
        return result

    # ------------------------------------------------------------------
    # Candidate tasks
    # ------------------------------------------------------------------

    def _task_intake(self, **kwargs) -> str | None:
        task = """Run a first-session intake for this candidate.

1. Assess their current profile — what's strong, what's missing
2. Brand discovery — identify UVP, unfair advantage, proudest achievements
3. Market positioning — how do they compare to top 1% in their target roles
4. Honest gap assessment
5. Action plan: 3 immediate wins + 30-day roadmap

Be specific and actionable. End with: "Here's exactly what we're doing next and why."

Return the UVP and brand_statement as a JSON block at the end:
```json
{"uvp": "...", "brand_statement": "..."}
```"""
        prompt = self._build_prompt(task)
        output = call_claude(prompt)
        if output:
            save_session(self.client_id, "intake", output)
            self._extract_and_save_brand(output)
        return output

    def _task_resume_analysis(self, **kwargs) -> str | None:
        target_role = kwargs.get("target_role", "")
        task = f"""Perform a comprehensive resume analysis for this candidate.
{f"Target role: {target_role}" if target_role else ""}

Provide:
1. **Strengths** — What's working well
2. **Weaknesses** — Gaps, weak language, missing quantification
3. **Achievement Mining** — Hidden wins that should be highlighted
4. **ATS Score Estimate** — How well this would pass automated screening
5. **Top 5 Immediate Fixes** — Quick wins to improve right now
6. **30-Day Improvement Roadmap**

Be specific, actionable, and honest. Format as clean markdown."""
        prompt = self._build_prompt(task)
        output = call_claude(prompt)
        if output:
            save_session(self.client_id, "resume_analysis", output)
        return output

    def _task_tailor_resume(self, **kwargs) -> str | None:
        job = kwargs.get("job", "")
        task = f"""Tailor this candidate's resume for the following target:
Target: {job}

Steps:
1. Research what top candidates look like for this role
2. Extract must-have keywords for this type of role
3. Map candidate's experience to requirements
4. Identify gaps — flag anything the candidate should confirm
5. Rewrite resume with achievement language and keyword matching
6. Provide ATS-optimized version (clean markdown)

Output:
## Keyword Analysis
(keywords found, missing, match score)

## Tailored Resume (ATS Version)
(full rewritten resume in clean markdown)

## Notes for Candidate
(gaps to address, things to confirm, interview prep points)"""

        extra = f"## Target Role\n{job}" if job else ""
        prompt = self._build_prompt(task, extra)
        output = call_claude(prompt)
        if output:
            # Save to resume/ subdir
            cdir = client_dir(self.client_id) / "resume"
            cdir.mkdir(parents=True, exist_ok=True)
            slug = re.sub(r'[^a-z0-9]+', '_', job.lower())[:40] if job else "general"
            ts = datetime.now().strftime("%Y%m%d")
            path = cdir / f"{slug}_{ts}.md"
            path.write_text(output)
            print(f"  Saved: {path}")
        return output

    def _task_linkedin(self, **kwargs) -> str | None:
        task = """Optimize this candidate's LinkedIn presence. Provide rewrites for:

1. **Headline** — Magnetic, keyword-rich, brand statement (max 220 chars)
2. **About Section** — First-person, hooks in first 3 lines, achievement-focused
3. **Experience Bullets** — Achievement language (rewrite top 2-3 roles)
4. **Skills** — Strategic top 50 skills list, ordered by importance
5. **Featured Section** — What to showcase and in what order
6. **Creator Mode** — Whether to activate and content strategy
7. **Connection Strategy** — Who to connect with, messaging templates

Format each section clearly in markdown."""
        prompt = self._build_prompt(task)
        output = call_claude(prompt)
        if output:
            save_session(self.client_id, "linkedin", output)
        return output

    def _task_brand(self, **kwargs) -> str | None:
        task = """Build a complete personal brand architecture for this candidate.

Deliver:
1. **Unique Value Proposition (UVP)** — What makes them irreplaceable (1-2 sentences)
2. **Brand Statement** — One-liner that defines them
3. **Unfair Advantage** — The combination only they have
4. **Target Audience** — Companies/roles/industries to focus on and why
5. **Positioning** — How to stand out against other candidates
6. **Content Strategy** — LinkedIn topics, frequency, format
7. **Elevator Pitch** — 30-second and 60-second versions

Return the UVP and brand_statement as a JSON block at the end:
```json
{"uvp": "...", "brand_statement": "..."}
```"""
        prompt = self._build_prompt(task)
        output = call_claude(prompt)
        if output:
            # Save to brand/ subdir
            brand_dir = client_dir(self.client_id) / "brand"
            brand_dir.mkdir(parents=True, exist_ok=True)
            (brand_dir / "positioning.md").write_text(output)
            self._extract_and_save_brand(output)
            save_session(self.client_id, "brand", output)
        return output

    def _task_portfolio(self, **kwargs) -> str | None:
        """Generate portfolio HTML for this candidate."""
        profile = load_profile(self.client_id)
        if not profile:
            print("[error] No profile found")
            return None
        from portfolio_generator import generate_portfolio
        output_dir = client_dir(self.client_id) / "portfolio"
        path = generate_portfolio(profile, output_dir)
        return f"Portfolio generated: {path}"

    # ------------------------------------------------------------------
    # Company tasks
    # ------------------------------------------------------------------

    def _task_screen_resumes(self, **kwargs) -> str | None:
        job_id = kwargs.get("job", "")
        if not job_id:
            print("[error] --job <job_id> required for screen_resumes")
            return None

        job = load_job(self.client_id, job_id)
        if not job:
            print(f"[error] Job {job_id} not found for {self.client_id}")
            return None

        # Collect candidate resumes from company's candidates/ dir
        cand_dir = client_dir(self.client_id) / "candidates"
        candidates_text = ""
        if cand_dir.exists():
            for f in cand_dir.glob("*.json"):
                cdata = json.loads(f.read_text())
                candidates_text += f"\n### {cdata.get('name', f.stem)}\n```json\n{json.dumps(cdata, indent=2)}\n```\n"

        task = f"""Screen all submitted resumes against this job description.

## Job: {job.get('title', '')}
```json
{json.dumps(job, indent=2)}
```

## Submitted Candidates
{candidates_text if candidates_text else "(No candidates submitted yet)"}

For each candidate:
1. ATS keyword match score (%)
2. Top 3 strengths for this role
3. Top 3 concerns/gaps
4. Recommendation: STRONG YES / YES / MAYBE / NO

Then provide a ranked shortlist with brief justification."""

        prompt = self._build_prompt(task)
        output = call_claude(prompt)
        if output:
            save_session(self.client_id, "screening", output, subdir="reports")
        return output

    def _task_write_jd(self, **kwargs) -> str | None:
        role = kwargs.get("role", "")
        if not role:
            print("[error] --role required for write_jd")
            return None

        profile = load_profile(self.client_id)
        task = f"""Write a compelling, inclusive job description for this role:
Role: {role}
Company: {profile.get('name', '')}
Industry: {profile.get('industry', '')}

The JD should:
1. Hook top talent in the first 2 sentences
2. Be inclusive (no gendered language, no unnecessary requirements)
3. List must-haves vs nice-to-haves separately
4. Include salary range placeholder
5. Highlight company culture and benefits
6. Be ATS-optimized with proper keywords
7. Be legally compliant

Also return a structured JSON block:
```json
{{"title": "...", "requirements": [...], "nice_to_have": [...], "description": "..."}}
```"""

        prompt = self._build_prompt(task)
        output = call_claude(prompt)
        if output:
            # Create job record
            job = create_job(self.client_id, role)
            # Try to extract structured data
            json_match = re.search(r'```json\s*({.*?})\s*```', output, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    job.update({k: v for k, v in data.items() if k in job})
                except json.JSONDecodeError:
                    pass
            job["description"] = output
            save_job(job)
            print(f"  Job created: {job['id']}")
            save_session(self.client_id, "write_jd", output, subdir="reports")
        return output

    def _task_weekly_report(self, **kwargs) -> str | None:
        # Gather company data
        jobs = list_jobs(self.client_id)
        cand_dir = client_dir(self.client_id) / "candidates"
        num_candidates = len(list(cand_dir.glob("*.json"))) if cand_dir.exists() else 0

        reports_dir = client_dir(self.client_id) / "reports"
        recent_reports = ""
        if reports_dir.exists():
            for f in sorted(reports_dir.glob("*.md"))[-3:]:
                recent_reports += f"\n### {f.stem}\n{f.read_text()[:500]}...\n"

        task = f"""Generate a weekly HR report for this company.

Active jobs: {len(jobs)}
Candidates in pipeline: {num_candidates}

## Recent Activity
{recent_reports if recent_reports else "(No prior reports)"}

Include:
1. Pipeline summary — candidates by stage
2. Open roles status
3. Key metrics (time-to-fill, candidate quality)
4. Recommendations for this week
5. Any flags or concerns

Format as a clean, executive-ready report."""

        prompt = self._build_prompt(task)
        output = call_claude(prompt)
        if output:
            save_session(self.client_id, "weekly_report", output, subdir="reports")
        return output

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_and_save_brand(self, output: str):
        """Extract UVP/brand_statement JSON from output and save to profile."""
        json_match = re.search(r'```json\s*({.*?})\s*```', output, re.DOTALL)
        if not json_match:
            return
        try:
            data = json.loads(json_match.group(1))
            profile = load_profile(self.client_id)
            if profile:
                if data.get("uvp"):
                    profile["uvp"] = data["uvp"]
                if data.get("brand_statement"):
                    profile["brand_statement"] = data["brand_statement"]
                save_profile(profile)
                # Also save UVP file
                brand_dir = client_dir(self.client_id) / "brand"
                brand_dir.mkdir(parents=True, exist_ok=True)
                (brand_dir / "uvp.md").write_text(
                    f"# Unique Value Proposition\n\n{data.get('uvp', '')}\n\n"
                    f"## Brand Statement\n\n{data.get('brand_statement', '')}\n"
                )
        except json.JSONDecodeError:
            pass


# ---------------------------------------------------------------------------
# Batch operations
# ---------------------------------------------------------------------------

def batch_weekly_checkin():
    """Send weekly check-in to all active candidates."""
    candidates = list_clients("candidate")
    print(f">> Weekly check-in for {len(candidates)} candidates")
    for c in candidates:
        aria = ARIA(c["id"])
        profile = load_profile(c["id"])
        if not profile:
            continue
        task = """Generate a weekly check-in message for this candidate.
Include:
1. Encouraging opener
2. Ask about job applications this week
3. Any responses or interviews?
4. What's blocking progress?
5. One skill to work on this week
6. Motivational close — remind them of their UVP and progress

Keep it warm, personal, and under 300 words. Format for WhatsApp (no markdown)."""
        prompt = aria._build_prompt(task)
        output = call_claude(prompt)
        if output:
            save_session(c["id"], "weekly_checkin", output)
            print(f"  {c['name']}: check-in generated")


def batch_portfolio_sync():
    """Regenerate portfolios for all candidates."""
    from portfolio_generator import generate_portfolio
    candidates = list_clients("candidate")
    print(f">> Portfolio sync for {len(candidates)} candidates")
    for c in candidates:
        profile = load_profile(c["id"])
        if not profile:
            continue
        output_dir = client_dir(c["id"]) / "portfolio"
        generate_portfolio(profile, output_dir)
        print(f"  {c['name']}: portfolio regenerated")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ARIA — AI Recruitment & Career Intelligence Agent (Multi-Tenant)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 aria.py --new-candidate --name "John Doe" --email "john@example.com"
  python3 aria.py --client cand_abc123 --task intake
  python3 aria.py --client cand_abc123 --task tailor_resume --job "Senior Engineer at Google"
  python3 aria.py --new-company --name "Acme Corp" --industry "Tech"
  python3 aria.py --client comp_xyz789 --task write_jd --role "Senior Engineer"
  python3 aria.py --list-clients
  python3 aria.py --batch weekly_checkin
""",
    )

    # Client creation
    parser.add_argument("--new-candidate", action="store_true", help="Create new candidate")
    parser.add_argument("--new-company", action="store_true", help="Create new company")
    parser.add_argument("--name", help="Client name")
    parser.add_argument("--email", help="Candidate email")
    parser.add_argument("--industry", help="Company industry")

    # Task execution
    parser.add_argument("--client", help="Client ID (cand_xxx or comp_xxx)")
    parser.add_argument("--task", help="Task to run")
    parser.add_argument("--job", help="Job ID or job description string")
    parser.add_argument("--role", help="Role title (for write_jd)")

    # Batch & admin
    parser.add_argument("--batch", help="Batch operation (weekly_checkin, portfolio_sync)")
    parser.add_argument("--list-clients", action="store_true", help="List all active clients")

    args = parser.parse_args()

    # --- Create candidate ---
    if args.new_candidate:
        if not args.name or not args.email:
            print("[error] --name and --email required for --new-candidate")
            sys.exit(1)
        cid = new_candidate_id()
        profile = create_candidate_profile(cid, args.name, args.email)
        save_profile(profile)
        register_client(cid, "candidate", args.name)
        print(f"[ok] Candidate created: {cid}")
        print(f"  Name: {args.name}")
        print(f"  Email: {args.email}")
        print(f"  Dir: {client_dir(cid)}")
        return

    # --- Create company ---
    if args.new_company:
        if not args.name:
            print("[error] --name required for --new-company")
            sys.exit(1)
        industry = args.industry or "General"
        cid = new_company_id()
        profile = create_company_profile(cid, args.name, industry)
        save_profile(profile)
        register_client(cid, "company", args.name)
        print(f"[ok] Company created: {cid}")
        print(f"  Name: {args.name}")
        print(f"  Industry: {industry}")
        print(f"  Dir: {client_dir(cid)}")
        return

    # --- List clients ---
    if args.list_clients:
        clients = list_clients()
        if not clients:
            print("No clients registered.")
            return
        print(f"\n{'ID':<20} {'Type':<12} {'Name':<25} {'Last Active'}")
        print("-" * 75)
        for c in clients:
            print(f"{c['id']:<20} {c['type']:<12} {c['name']:<25} {c.get('last_active', 'N/A')[:19]}")
        print(f"\nTotal: {len(clients)} clients")
        return

    # --- Batch operations ---
    if args.batch:
        batches = {
            "weekly_checkin": batch_weekly_checkin,
            "portfolio_sync": batch_portfolio_sync,
        }
        handler = batches.get(args.batch)
        if not handler:
            print(f"[error] Unknown batch: {args.batch}")
            print(f"  Available: {', '.join(batches.keys())}")
            sys.exit(1)
        handler()
        return

    # --- Run task for client ---
    if args.client and args.task:
        client = find_client(args.client)
        if not client:
            print(f"[error] Client not found: {args.client}")
            sys.exit(1)

        aria = ARIA(args.client)
        kwargs = {}
        if args.job:
            kwargs["job"] = args.job
        if args.role:
            kwargs["role"] = args.role

        result = aria.run_task(args.task, **kwargs)
        if result:
            print(f"\n{result}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
