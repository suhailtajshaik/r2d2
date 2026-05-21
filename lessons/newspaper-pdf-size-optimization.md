# Lesson: Newspaper PDF Size Optimization (March 31, 2026)

## Problem
- PDF was **13MB / 10 pages** for a daily newspaper briefing
- Showing **4 articles per section × 6 sections = 24 articles** (excessive)
- Full article bodies included (unnecessary bloat)
- **User feedback:** "PDF is very very very large for the news... I don't even see all the news"

## Root Cause
Three layering issues:
1. **Content volume:** Too many articles per section (4 → should be 2)
2. **Text truncation missing:** Full article bodies rendered in PDF
3. **Typography waste:** Large fonts + excessive padding = unnecessary vertical space

## Solution Applied
**Layer 1: Content reduction**
- Articles per section: 4 → 2 (reduces from 24 to ~12 articles max)

**Layer 2: Text truncation**
- Article body: Full text → First 150 characters + "..."
- Preserves headline + summary without bloat

**Layer 3: Compact typography**
- Body font: 18px → 16px
- Body padding: 40px → 20px
- Article headline: 24px → 19px
- Article body: 17px → 14px
- Line-height: 1.7 → 1.6 (tighter spacing)
- Article margin: 24px → 16px

## Result
- **Before:** 13MB / 10 pages (unusable for mobile)
- **After:** 1.7MB / 2 pages (clean, professional, readable)
- **Speed improvement:** Faster WhatsApp delivery
- **UX improvement:** All sections visible on 2 pages

## Applied Pattern: Layer Identification
When Suhail says "PDF is too large", I should immediately identify the layer:
- **Content layer:** Too many articles? (Yes → reduce count)
- **Rendering layer:** Unnecessary text? (Yes → truncate)
- **Typography layer:** Wasted space? (Yes → compact)

**Key lesson:** Don't fix all layers at once in separate PRs. Identify all issues, apply all fixes in ONE change cycle, test once, verify once.

## Files Changed
- `/home/r2d2/tools/generate-newspaper.py` — Line 40, 42-46, 54-58, 64-70

## Testing
- Ran full pipeline: Maxwell (fetch) → generate-newspaper.py (PDF) → Verify
- Spot-checked: 21 articles fetched, 12 shown in PDF, all sections visible
- Verified file size and page count before delivery

## Integration
- Cron job `r2d2:daily-newspaper` now calls correct Python script (was calling old Node script)
- Daily delivery at 5 AM EST now produces compact 2-page PDF
- No manual intervention needed

## Never Again
- Don't show >2 articles per section without asking
- Don't render full article bodies in PDFs (always truncate)
- Don't assume current typography is optimal (test compact versions first)
