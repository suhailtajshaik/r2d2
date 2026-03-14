# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

### Send Document Skill
- Location: `skills/send-document/SKILL.md`
- **NEVER send .md files directly** — phones can't open them
- Convert .md → PDF first: `skills/send-document/scripts/md-to-pdf.sh input.md /tmp/output.pdf`
- Always set `filename` and `mimeType` when sending files via message tool
- PDF mimeType: `application/pdf`

### PDF Generation Preferences
- **No headers or footers** — only page numbers (bottom center, small gray text)
- Uses Puppeteer with custom footer template
- Script: `skills/send-document/scripts/md-to-pdf.sh`

---

Add whatever helps you do your job. This is your cheat sheet.
