# 🤖 Domain-Specific Agents Index

A collection of specialized AI agents for knowledge expansion, voice interaction, and video generation.

## New Agents (2026-03-20)

### 1. 🧠 Yoda Learning Loop Agent
**Status:** ✅ Ready for deployment
**Location:** `/home/r2d2/brain/agents/yoda/`

Autonomous knowledge expansion and continuous learning.

- **Purpose:** Monitor gaps, identify trends, synthesize guides
- **Schedule:** 4x daily (2 AM, 8 AM, 2 PM, 8 PM EST)
- **Output:** Knowledge guides in `/home/r2d2/projects/yoda/knowledge/`
- **Integration:** Updates MEMORY.md with learnings
- **Setup:** Run cron scheduler with 4 lines

**Key Files:**
- `yoda_learning_agent.py` - Main learning loop
- `yoda_scheduler.sh` - Cron automation
- `README.md` - Full setup guide

**Quick Start:**
```bash
cd /home/r2d2/brain/agents/yoda
chmod +x yoda_scheduler.sh
crontab -e  # Add 4 schedule lines
python3 yoda_learning_agent.py  # Test run
```

---

### 2. 📞 Voice Agent (Vapi)
**Status:** 🔧 Ready for setup
**Location:** `/home/r2d2/brain/agents/voice/`

Personal voice AI assistant available 24/7 via phone.

- **Purpose:** Voice tasks, briefings, status checks, memos
- **Access:** Call phone number (purchased from Vapi)
- **Features:** Intent detection, context awareness, TTS
- **Integration:** Reads MEMORY.md, task list, daily context

**Key Files:**
- `voice_agent_webhook.py` - Webhook server (receives Vapi calls)
- `voice_context_system.py` - Context retrieval (template included)
- `voice_agent_cli.py` - Local testing (template)
- `README.md` - Complete setup guide

**Quick Start:**
```bash
# 1. Sign up at https://vapi.ai
# 2. Get API key and phone number
# 3. Set environment variables
export VAPI_API_KEY=sk_...
export VAPI_PHONE_ID=...
export VAPI_WEBHOOK_SECRET=...

# 4. Deploy webhook
cd /home/r2d2/brain/agents/voice
python3 voice_agent_webhook.py
```

---

### 3. 🎬 Video Clone Agent (HeyGen)
**Status:** 🔧 Ready for setup
**Location:** `/home/r2d2/brain/agents/video/`

Generate talking head videos with AI avatar.

- **Purpose:** Product announcements, tutorials, YouTube content
- **Output:** MP4 videos in `/home/r2d2/videos/`
- **Features:** Auto-script writing, batch generation, customization
- **Ready-to-Upload:** Direct to YouTube or CDN

**Key Files:**
- `video_agent.py` - Main agent (script writer, generator, scheduler)
- `README.md` - Complete setup guide

**Quick Start:**
```bash
# 1. Sign up at https://heygen.com
# 2. Get API key
# 3. Choose/create avatar

# 4. Set environment variables
export HEYGEN_API_KEY=sk_...
export HEYGEN_AVATAR_ID=default_male

# 5. Generate a video
cd /home/r2d2/brain/agents/video
python3 video_agent.py
```

---

## Existing Agents

| Agent | Location | Purpose | Status |
|-------|----------|---------|--------|
| **Aria** | `/home/r2d2/brain/agents/aria/` | Information retrieval | ✅ Active |
| **Maxwell** | `/home/r2d2/brain/agents/maxwell/` | Task/project management | ✅ Active |
| **Guardian** | `/home/r2d2/brain/agents/guardian/` | Security monitoring | ✅ Active |
| **Research** | `/home/r2d2/brain/agents/research/` | Deep research automation | ✅ Active |
| **Analytics** | `/home/r2d2/brain/agents/analytics/` | Data analysis | ✅ Active |

---

## Quick Deployment Guide

### Phase 1: Yoda (Immediate)
```bash
# 1. Make scheduler executable
chmod +x /home/r2d2/brain/agents/yoda/yoda_scheduler.sh

# 2. Add to crontab
crontab -e
# Paste these 4 lines:
# 0 2 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
# 0 8 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
# 0 14 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
# 0 20 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh

# 3. Test
python3 /home/r2d2/brain/agents/yoda/yoda_learning_agent.py

# 4. Monitor
tail -f /home/r2d2/.openclaw/workspace/memory/yoda_learning_*.log
```

### Phase 2: Voice Agent (Next Week)
```bash
# 1. Sign up for Vapi: https://vapi.ai
# 2. Get API key and phone number
# 3. Create .env file
cat > /home/r2d2/brain/agents/voice/.env << EOF
VAPI_API_KEY=sk_...
VAPI_PHONE_ID=...
VAPI_WEBHOOK_SECRET=...
EOF

# 4. Deploy webhook (production)
# Use systemd or Docker to keep it running 24/7

# 5. Test: Call your Vapi phone number
# "Create a task to test the voice agent"
```

### Phase 3: Video Agent (Following Week)
```bash
# 1. Sign up for HeyGen: https://heygen.com
# 2. Get API key
# 3. Create .env file
cat > /home/r2d2/brain/agents/video/.env << EOF
HEYGEN_API_KEY=sk_...
HEYGEN_AVATAR_ID=default_male
HEYGEN_VOICE_ID=male_neutral
EOF

# 4. Install dependencies
pip install requests python-dotenv boto3

# 5. Test
python3 /home/r2d2/brain/agents/video/video_agent.py
```

---

## Integration Map

```
                    ┌─────────────────┐
                    │   SUHAIL'S      │
                    │  VOICE CALLS    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  VOICE AGENT    │ 📞 Vapi
                    │  (24/7 Access)  │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼───┐         ┌─────▼─────┐     ┌──────▼──────┐
    │ CREATE  │         │  CHECK    │     │ GET DAILY   │
    │ TASKS   │         │  STATUS   │     │ BRIEFING    │
    │         │         │           │     │             │
    └────┬───┘         └─────┬─────┘     └──────┬──────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │  CONTEXT SYSTEM             │
              │  Reads: MEMORY.md           │
              │         Tasks               │
              │         Calendar            │
              └──────────┬───────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───▼────┐    ┌──────▼──────┐  ┌────▼────┐
    │  YODA  │    │  MAXWELL    │  │ ARIA    │
    │ Learning    │  Project    │  │ Search  │
    │ Agent  │    │  Management │  │ & Info  │
    └────────┘    └─────────────┘  └─────────┘

                 ┌──────────────┐
                 │ VIDEO AGENT  │ 🎬 HeyGen
                 │ Script→Video │
                 │ for YouTube  │
                 └──────────────┘
                        ▲
                        │
                   ┌────┴────┐
                   │ From    │
                   │ Guides  │
                   │ & Memos │
                   └─────────┘
```

---

## File Structure

```
/home/r2d2/brain/agents/
├── yoda/
│   ├── yoda_learning_agent.py
│   ├── yoda_scheduler.sh
│   ├── learning_state.json
│   ├── last_run.json
│   └── README.md
├── voice/
│   ├── voice_agent_webhook.py
│   ├── voice_context_system.py (template)
│   ├── voice_agent_cli.py (template)
│   ├── .env (secrets - not in git)
│   ├── call_log.jsonl
│   ├── state.json
│   ├── tasks.json
│   ├── memos/
│   │   ├── abc123.json
│   │   └── ...
│   └── README.md
├── video/
│   ├── video_agent.py
│   ├── .env (secrets - not in git)
│   ├── schedule.json
│   ├── scripts/
│   │   ├── 20260320_143000_intro.txt
│   │   └── ...
│   ├── metadata/
│   │   ├── video_abc123.json
│   │   └── ...
│   └── README.md
└── AGENTS_INDEX.md (this file)

/home/r2d2/projects/yoda/knowledge/
├── ai_agents_and_autonomous_systems.md
├── voice_ai_and_multimodal_interfaces.md
├── video_synthesis_and_deepfakes.md
└── ...

/home/r2d2/videos/
├── video_abc123.mp4
├── video_def456.mp4
└── ...
```

---

## Monitoring & Maintenance

### Daily Checks

```bash
# Yoda learning status
cat /home/r2d2/brain/agents/yoda/learning_state.json | jq .

# Voice agent calls today
cat /home/r2d2/brain/agents/voice/call_log.jsonl | \
  grep "$(date +%Y-%m-%d)" | wc -l

# Video generation status
python3 -c "
from sys import path
path.insert(0, '/home/r2d2/brain/agents/video')
from video_agent import VideoManager
manager = VideoManager()
for v in manager.list_videos()[-5:]:
    print(f\"{v['title']}: {v['status']}\")
"
```

### Weekly Maintenance

```bash
# Review Yoda digest
cat /home/r2d2/brain/agents/yoda/digest_*.md

# Archive old call logs
find /home/r2d2/brain/agents/voice -name "*.jsonl" \
  -mtime +30 -exec gzip {} \;

# Check video storage usage
du -sh /home/r2d2/videos/
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Yoda not running | Check crontab: `crontab -l \| grep yoda` |
| Voice webhook down | Check service: `systemctl status voice-webhook` |
| Video generation slow | Check HeyGen API status; may be queue |
| Memory updates missing | Verify MEMORY.md write permissions |
| Script creation failing | Check `/home/r2d2/brain/agents/*/scripts/` directory exists |

---

## Next Steps

1. **This Week:** Deploy Yoda learning loop
   - [ ] Make scheduler executable
   - [ ] Add to crontab
   - [ ] Verify first run logs

2. **Next Week:** Deploy Voice Agent
   - [ ] Sign up for Vapi
   - [ ] Deploy webhook server
   - [ ] Test with first call

3. **Following Week:** Deploy Video Agent
   - [ ] Sign up for HeyGen
   - [ ] Create API key
   - [ ] Test video generation

---

## Support & Documentation

- **Yoda README:** `/home/r2d2/brain/agents/yoda/README.md`
- **Voice README:** `/home/r2d2/brain/agents/voice/README.md`
- **Video README:** `/home/r2d2/brain/agents/video/README.md`
- **Agent Index:** This file

---

**Created:** 2026-03-20
**Updated:** 2026-03-20
**Maintainer:** R2D2 (Suhail's Personal Assistant)
**Status:** 3 New Agents Ready for Deployment
