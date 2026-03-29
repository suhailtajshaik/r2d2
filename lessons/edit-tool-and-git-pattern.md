# Lesson: Edit Tool + Git Commit Anti-Pattern
**Date:** March 29, 2026
**Context:** Tried to Edit MEMORY.md after git commit had already updated it
**Status:** ❌ MISTAKE MADE → ✅ RULE ESTABLISHED

---

## The Mistake

### What I Did
1. Used git commit to update MEMORY.md (via editing another file and committing)
2. Then tried to use Edit tool on MEMORY.md with old text that no longer matched
3. Edit tool failed: "Could not find the exact text"
4. Created noise and confusion

### Why It Was Wrong
- **Two tools modifying same file:** Git commit changed the file, then Edit tool tried to find old content
- **State mismatch:** After git commit, the exact old text no longer existed in the file
- **Noise for user:** Suhail saw an error that shouldn't have existed

---

## The Pattern (Why It Happened)

I did this sequence:
```
1. Made changes and committed to git
2. Tried to make more changes with Edit tool
3. Edit tool searched for old text
4. Old text didn't exist (git commit changed it)
5. Edit tool failed
6. User sees error message
```

The problem: **Two different modification paths on the same file**

---

## The Rule (Prevention)

### CHOOSE ONE METHOD PER FILE PER SESSION

**Option A: Use Edit tool only**
```
→ Read the file
→ Identify exact old text
→ Use Edit tool to change it
→ At end of session: git commit once
✅ Clean, single-source-of-truth
```

**Option B: Use git commands directly**
```
→ Use bash commands to modify file
→ git add
→ git commit immediately
✅ Direct, no tool state confusion
```

**❌ NEVER: Mix both methods on same file**
```
❌ Edit tool to change file A
❌ Git commit to change file A
❌ Try Edit tool again on file A
= Guaranteed failure
```

### Specific Prevention Rule

**IF** I've already done a git commit on a file in this session  
**THEN** Do NOT use Edit tool on that file again  
**ELSE** I'll get "exact text not found" errors

---

## Applied Going Forward

### When Making Multiple Changes to Same File

**Correct approach:**
```
1. Read file to find exact text
2. Use Edit tool to make first change
3. Use Edit tool to make second change
4. At end: git commit once with all changes
```

**Wrong approach (what I did):**
```
1. Edit one part
2. git commit (file updated)
3. Try to Edit another part
4. Tool fails because old text changed
❌ Noise
```

### Decision Tree

```
Do I need to edit a file?
  ├─ First time editing this file this session?
  │  └─ YES → Use Edit tool
  │
  ├─ Already used Edit tool on this file?
  │  ├─ YES → Use Edit tool again (before git commit)
  │  └─ NO → Continue
  │
  ├─ Already git committed this file?
  │  ├─ YES → Read file again, use bash/exec to edit if needed
  │  └─ NO → Use Edit tool
  │
  └─ At end of all edits: git commit once
```

---

## Files Affected

**This incident:**
- Tried Edit on MEMORY.md after git commit had already updated it
- Could have affected multiple files if I'd continued

**Prevention:**
- Single-tool rule per file per session
- One git commit per batch of changes

---

## Quality Gate (Before Each Session)

- ✓ Did I use Edit tool OR git, not both, on same file?
- ✓ Did I commit once at the end, not multiple times?
- ✓ Did I avoid trying to Edit after git commit?
- ✓ Is there any tool noise/errors from state confusion?

---

## Why This Matters

- **For users:** No confusing error messages about "exact text not found"
- **For clarity:** One tool per job = predictable, clear
- **For debugging:** No state confusion from mixed approaches
- **For professionalism:** No noise in output

---

## Summary

✅ **Learned:** Don't use Edit tool after git commit on same file
✅ **Learned:** Choose one method per file per session
✅ **Learned:** Batch all edits before final git commit

**Next time:** Edit all changes first, then commit once. No tool noise.
