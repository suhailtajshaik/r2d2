# Prompt Studio Dev — Access & Review Guide

## Current Status
- **Branch:** `development`
- **Changes:** Rey design improvements (colors, fonts, spacing)
- **Status:** Ready for review

## How to Access

### Option 1: SSH Tunnel (Recommended for secure review)
```bash
# From your local machine
ssh -L 3001:localhost:3001 r2d2@srv1305247.lab.dflow.com

# Then open in browser
http://localhost:3001
```

### Option 2: Direct Docker Access (if you have VPS access)
```bash
# On VPS
docker run -d -p 3001:3000 --name prompt-studio-dev prompt-studio:dev
```

### Option 3: Review from Git
```bash
# Clone and review changes
git clone https://github.com/suhailtajshaik/prompt-studio.git
git checkout development
git diff master development
```

## What Changed

### Design Updates (Rey's Work)
✅ **Colors:** Purple (#6C5CE7) → Indigo (#6366F1)  
✅ **Fonts:** Inter → System fonts (-apple-system, Segoe UI, Roboto)  
✅ **Spacing:** Increased padding for breathing room  
✅ **Components:** Removed gradient overlays, simplified shadows  
✅ **Aesthetic:** Now aligns with Stripe/Linear design  

### Files Modified
- `src/index.css` — Global styles, color variables
- `src/components/*.jsx` — Component styling
- `vite.config.js` — Build configuration

## Verification Checklist

Before going to production, verify:

- [ ] Colors are consistent (indigo #6366F1)
- [ ] Fonts are system fonts (no Inter/Roboto)
- [ ] Buttons/cards have no gradient overlays
- [ ] Spacing is generous (padding increased)
- [ ] Responsive design works (test on mobile)
- [ ] All interactive elements work
- [ ] No console errors (check DevTools)

## Running Locally

### Install & Run
```bash
cd /home/r2d2/projects/prompt-studio
git checkout development
npm install
npm run dev
```

Then open: `http://localhost:5173`

### Build & Test
```bash
npm run build
npm run preview
```

## Deployment to Production

When ready to merge to production:

```bash
# 1. Run verification
/home/r2d2/tools/verify-deployment.sh ./dist prompt-studio

# 2. If passes, commit and merge
git add .
git commit -m "feat: apply Rey design improvements"
git checkout master
git merge development

# 3. Deploy to production
docker build -t prompt-studio:latest .
docker stop prompt-studio
docker rm prompt-studio
docker run -d -p 3000:80 --name prompt-studio prompt-studio:latest
```

## Questions or Issues?

- **Design questions?** Check Rey's audit report: `/home/r2d2/projects/prompt-studio/DESIGN_AUDIT_REPORT.md`
- **Deployment questions?** See Yoda's guide: `/home/r2d2/tools/DEPLOYMENT_TROUBLESHOOTING_GUIDE.md`
- **Technical questions?** Ask 3PO (Claude Code)

## Next Steps

1. ✅ Review the changes (this doc)
2. ⏳ Decide: approve or request changes?
3. If approved → Merge to master → Deploy to production

---

**Dev Changes:** `development` branch  
**Production:** `master` branch  
**Deployed at:** http://localhost:3001 (when running)
