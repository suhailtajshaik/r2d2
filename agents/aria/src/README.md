# ARIA — AI Recruitment & Career Intelligence Agent

Multi-tenant AI agent that serves **multiple companies AND candidates simultaneously**. One instance, full data isolation per client.

## Architecture

```
clients/
  registry.json              # All active clients
  companies/
    <company_id>/
      profile.json           # Company info
      jobs/                  # Job descriptions
      candidates/            # Screened applicants
      reports/               # Weekly HR reports
  candidates/
    <candidate_id>/
      profile.json           # Candidate data
      resume/                # Master + tailored versions
      portfolio/             # Generated HTML portfolio
      brand/                 # UVP, positioning
      sessions/              # Session logs
```

## Quick Start

```bash
# Create a candidate
python3 aria.py --new-candidate --name "John Doe" --email "john@example.com"

# Create a company
python3 aria.py --new-company --name "Acme Corp" --industry "Tech"

# List all clients
python3 aria.py --list-clients
```

## Candidate Tasks

```bash
python3 aria.py --client cand_xxx --task intake           # First session intake
python3 aria.py --client cand_xxx --task resume_analysis   # Deep resume analysis
python3 aria.py --client cand_xxx --task tailor_resume --job "Senior Engineer at Google"
python3 aria.py --client cand_xxx --task linkedin          # LinkedIn optimization
python3 aria.py --client cand_xxx --task brand             # Personal brand architecture
python3 aria.py --client cand_xxx --task portfolio         # Generate portfolio HTML
```

## Company Tasks

```bash
python3 aria.py --client comp_xxx --task write_jd --role "Senior Engineer"
python3 aria.py --client comp_xxx --task screen_resumes --job job_xxx
python3 aria.py --client comp_xxx --task weekly_report
```

## Batch Operations

```bash
python3 aria.py --batch weekly_checkin    # Generate check-ins for all candidates
python3 aria.py --batch portfolio_sync    # Regenerate all portfolios
```

## ATS Analyzer (Standalone)

```bash
python3 ats_analyzer.py <job_description.txt> <resume.txt>
```

## Docker

```bash
docker compose up -d --build
docker compose run aria --new-candidate --name "Test" --email "test@test.com"
```

## Stack

- Python 3.12
- Claude CLI (Claude Code) for AI tasks
- Tailwind CDN for portfolio generation
- No external dependencies beyond standard library

## Files

| File | Purpose |
|------|---------|
| `aria.py` | Main multi-tenant agent + CLI |
| `schema.py` | Client schemas, registry, UUID generation |
| `ats_analyzer.py` | ATS keyword scoring (standalone) |
| `portfolio_generator.py` | Static portfolio HTML generator |
| `templates/` | Jinja2 templates for resumes/cover letters |
