---
name: send-document
description: "Send documents and files to users via messaging channels (WhatsApp, Telegram, etc.) with proper filenames, formats, and readability. Use when: (1) User asks to send/share a file, (2) User requests a document like .md, .pdf, .txt, .json, (3) User says 'send me the file' or 'share the plan', (4) Any file delivery over messaging. Keywords: send file, share document, send me, export, download, deliver file."
---

# Send Document

## Overview

Handle file delivery over messaging channels. Key rule: **always ensure the recipient can open and read the file on mobile**. Markdown files (.md) must be converted to PDF before sending since phones can't render them.

## Quick Reference

| File Type | Action Before Sending |
|-----------|----------------------|
| `.md` | Convert to PDF using `md-to-pdf.sh` |
| `.pdf` | Send directly |
| `.txt` | Send directly |
| `.json` | Send directly (or convert to readable format if requested) |
| `.csv` | Send directly |
| `.png/.jpg` | Send directly as image |
| Code files | Convert to PDF for readability, or send as-is if user is technical |

## Core Workflow

### Step 1: Determine file type and convert if needed

For `.md` files, always convert to PDF:

```bash
/home/r2d2/.openclaw/workspace/skills/send-document/scripts/md-to-pdf.sh /path/to/input.md /tmp/output.pdf
```

### Step 2: Send with proper metadata

Always include these parameters in the `message` tool call:
- `filePath` — absolute path to the file
- `filename` — proper name WITH extension (e.g., `sellbridge-plan.pdf`)
- `mimeType` — correct MIME type for the file
- `message` — the filename or brief description

### MIME Types Reference

| Extension | mimeType |
|-----------|----------|
| `.pdf` | `application/pdf` |
| `.txt` | `text/plain` |
| `.json` | `application/json` |
| `.csv` | `text/csv` |
| `.png` | `image/png` |
| `.jpg` | `image/jpeg` |
| `.mp4` | `video/mp4` |
| `.mp3` | `audio/mpeg` |
| `.doc` | `application/msword` |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| `.zip` | `application/zip` |

## Critical Rules

- **Never send .md files directly** — phones can't open them. Always convert to PDF first.
- **Always set `filename`** — with the correct extension so the recipient sees a proper filename.
- **Always set `mimeType`** — ensures the messaging platform handles the file correctly.
- **Use `/tmp/` for converted files** — don't pollute the workspace with temporary PDFs.
- **Keep original filename** — if source is `plan.md`, send as `plan.pdf` (same base name).

## Dependencies

- **google-chrome-stable**: Used for headless PDF generation (already installed)
- **Node.js**: For markdown-to-HTML conversion (already installed)
- **md-to-pdf.sh script**: Located at `skills/send-document/scripts/md-to-pdf.sh`
