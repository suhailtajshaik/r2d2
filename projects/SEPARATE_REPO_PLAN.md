# Research Tool — Separate Repository Plan

**Move research-tool to its own standalone GitHub repository**

---

## Rationale

- `research-tool` is fully independent (no dependencies on news-engine)
- `newspaper-research` depends on `research-tool` but is news-engine specific
- Separating allows:
  - Standalone use for other projects
  - Version independent from news-engine
  - Community contributions
  - Cleaner separation of concerns

---

## Repository Plan

### research-tool (NEW REPO)
**GitHub:** `suhailtajshaik/research-tool`
- Standalone web research using Playwright + Chrome
- No dependencies on news-engine
- MIT license
- Can be used in any research/verification project

**Files to move:**
```
research-tool/
├── README.md
├── DEPLOY.md
├── main.py
├── requirements.txt
├── config.yaml
└── research_tool/
    ├── __init__.py
    ├── engine.py
    ├── scraper.py
    └── analyzer.py
```

### newspaper-research (STAYS in news-engine)
**Location:** `/home/r2d2/projects/news-engine/newspaper-research/`
- Wrapper around research-tool for news-engine
- Imports research-tool as dependency
- Specific to newspaper pipeline

---

## Migration Steps

1. **Create new GitHub repo**
   ```bash
   gh repo create research-tool --public --source=/home/r2d2/projects/research-tool
   ```

2. **Push to GitHub**
   ```bash
   cd /home/r2d2/projects/research-tool
   git init
   git add .
   git commit -m "Initial commit: research-tool v1.0"
   git remote add origin https://github.com/suhailtajshaik/research-tool.git
   git push -u origin main
   ```

3. **Update newspaper-research to depend on published version**
   ```
   requirements.txt:
   git+https://github.com/suhailtajshaik/research-tool.git@main
   ```

4. **Or keep local development link**
   ```
   requirements.txt:
   -e /home/r2d2/projects/research-tool
   ```

---

## Benefits

✅ research-tool can be used standalone
✅ newspaper-research is news-engine specific
✅ Can be version-pinned independently
✅ Community can contribute to research-tool
✅ Clean separation of concerns

---

## TODO

- [ ] Create GitHub repo: `suhailtajshaik/research-tool`
- [ ] Push initial code
- [ ] Update newspaper-research to import from published repo
- [ ] Document in README
- [ ] Add to portfolio/projects list

---

**Status:** Plan documented. Ready to execute when needed.
