# 🚀 Domain-Specific Agents Deployment Guide

Complete step-by-step deployment instructions for the three new agents.

## Overview

Three specialized agents are now ready for deployment:
1. **Yoda Learning Loop** - Autonomous knowledge expansion
2. **Voice Agent (Vapi)** - 24/7 phone access
3. **Video Clone Agent (HeyGen)** - AI avatar video generation

**Total Deployment Time:** ~2-3 weeks (phased approach)

---

## Phase 1: Yoda Learning Loop (Week 1) ⏰

**Timeline:** Immediate - Can be deployed in 15 minutes
**Cost:** Free (runs locally)
**Dependencies:** None (Python only)

### Step 1: Verify Installation

```bash
cd /home/r2d2/brain/agents/yoda
python3 -c "import os; print('Python OK')"
```

### Step 2: Make Scheduler Executable

```bash
chmod +x /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
ls -la /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
# Should show: -rwxr-xr-x
```

### Step 3: Test Local Run

```bash
python3 /home/r2d2/brain/agents/yoda/yoda_learning_agent.py
```

**Expected Output:**
```
🧠 Yoda Learning Loop Starting...
⏰ 2026-03-20T21:57:29.634246

📊 Detecting knowledge gaps...
Found 10 gap areas

🔍 Identifying trending topics...
Trending search strategy: Monitor emerging topics via web search

📚 Reviewing existing guides...
Reviewed 29 guides

📝 Updating knowledge base...
✅ Created: AI agents and autonomous systems
✅ Created: Voice AI and multimodal interfaces
✅ Created: Video synthesis and deepfakes

✨ Yoda Learning Loop Complete!
```

### Step 4: Install Cron Schedule

Open crontab editor:

```bash
crontab -e
```

Add these **4 lines** at the end:

```cron
# Yoda Learning Loop - 4 times daily
0 2 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
0 8 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
0 14 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
0 20 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
```

Save and exit (Ctrl+O, Ctrl+X in nano).

### Step 5: Verify Cron Schedule

```bash
crontab -l | grep yoda
```

**Expected Output:**
```
0 2 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
0 8 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
0 14 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
0 20 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
```

### Step 6: Monitor First Run

Wait for next scheduled time or check logs manually:

```bash
# View logs
tail -f /home/r2d2/.openclaw/workspace/memory/yoda_learning_*.log

# Check state
cat /home/r2d2/brain/agents/yoda/learning_state.json | jq .

# List created guides
ls /home/r2d2/projects/yoda/knowledge/ | tail -5
```

### ✅ Phase 1 Complete!

Yoda is now running 4 times daily automatically. Verify with:

```bash
# Check next run from cron logs
sudo journalctl -u cron -f

# Or check logs tomorrow
cat /home/r2d2/.openclaw/workspace/memory/yoda_learning_$(date +%Y-%m-%d).log
```

---

## Phase 2: Voice Agent (Week 2) 📞

**Timeline:** 3-5 days for setup
**Cost:** $10-20/month (phone number rental)
**Dependencies:** Vapi account + webhook server

### Step 1: Sign Up for Vapi

1. Go to https://vapi.ai
2. Create account (Google OAuth fastest)
3. Verify email
4. Navigate to Dashboard

### Step 2: Configure Vapi Settings

In Vapi Dashboard:

1. **Voice Settings**
   - Model: OpenAI GPT-4
   - TTS: ElevenLabs
   - Voice: "Male Neutral" (or preferred)
   - Language: English (US)

2. **API Keys**
   - Settings → API Keys
   - Create new key
   - Copy key (starts with `sk_`)

3. **Phone Number**
   - Phone Numbers → Purchase
   - Select US country
   - $10-20/month
   - Complete purchase
   - Note: Phone number and phone ID

### Step 3: Create Environment File

```bash
cd /home/r2d2/brain/agents/voice
cat > .env << 'EOF'
VAPI_API_KEY=sk_your_api_key_here
VAPI_PHONE_ID=your_phone_id_here
VAPI_WEBHOOK_SECRET=your_webhook_secret_here
OPENAI_API_KEY=sk_your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
EOF

chmod 600 .env
```

### Step 4: Install Dependencies

```bash
cd /home/r2d2/brain/agents/voice
pip install flask python-dotenv requests
```

### Step 5: Set Up Webhook Endpoint

**Option A: Local Development (Testing)**

```bash
# Terminal 1: Start webhook
cd /home/r2d2/brain/agents/voice
python3 -m flask run --port 5000
# Output: Running on http://127.0.0.1:5000

# Terminal 2: Use ngrok tunnel
brew install ngrok
ngrok http 5000
# Output: https://xxxx-xx-xxx-xxx-xx.ngrok.io
```

**Option B: Production (Using ngrok permanent URL)**

```bash
ngrok config add-authtoken YOUR_NGROK_AUTH_TOKEN
ngrok http 5000 --domain=your-custom-domain.ngrok.io
```

**Option C: Production (VPS/Server)**

Deploy to your OpenClaw VPS:

```bash
# Install systemd service
sudo cat > /etc/systemd/system/voice-webhook.service << 'EOF'
[Unit]
Description=Voice Agent Webhook Server
After=network.target

[Service]
Type=simple
User=r2d2
WorkingDirectory=/home/r2d2/brain/agents/voice
EnvironmentFile=/home/r2d2/brain/agents/voice/.env
ExecStart=/usr/bin/python3 /home/r2d2/brain/agents/voice/voice_webhook_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable voice-webhook
sudo systemctl start voice-webhook
```

### Step 6: Configure Vapi Webhook

In Vapi Dashboard:

1. **Settings** → **Webhooks**
2. **Endpoint URL:** `https://your-domain.com/voice-webhook`
3. **Events:** `call.started`, `call.ended`
4. **Secret:** Copy from your `.env` file `VAPI_WEBHOOK_SECRET`
5. **Save**

Should show: ✅ Active

### Step 7: Test Webhook

```bash
# Test local endpoint
curl -X GET http://127.0.0.1:5000/
# Should return 404 (GET not allowed)

# Webhook should be ready for Vapi calls
```

### Step 8: Test Voice Agent

Call your Vapi phone number:

```
+1 (XXX) XXX-XXXX
```

Try these voice commands:

1. **Create Task:**
   "Create a task to review the voice agent setup"
   → Agent: "Task created!"

2. **Check Status:**
   "What's the status of the Yoda agent?"
   → Agent: "Checking... [status]"

3. **Get Briefing:**
   "Give me my daily briefing"
   → Agent reads: [your schedule and updates]

4. **Voice Memo:**
   "Record a memo: Remember to test the video agent"
   → Agent: "Memo saved!"

### Step 9: Monitor Calls

```bash
# View incoming calls
tail -f /home/r2d2/brain/agents/voice/call_log.jsonl

# Count calls today
cat /home/r2d2/brain/agents/voice/call_log.jsonl | \
  grep "$(date +%Y-%m-%d)" | wc -l

# View memos
ls /home/r2d2/brain/agents/voice/memos/
cat /home/r2d2/brain/agents/voice/memos/[id].json
```

### ✅ Phase 2 Complete!

Voice agent is 24/7 accessible via phone. Test with:

```bash
# Call Vapi phone number
# Monitor logs
tail -f /home/r2d2/brain/agents/voice/call_log.jsonl
```

---

## Phase 3: Video Agent (Week 3) 🎬

**Timeline:** 2-3 days for setup
**Cost:** $10-50/month (API access + usage)
**Dependencies:** HeyGen account

### Step 1: Sign Up for HeyGen

1. Go to https://heygen.com
2. Create account (Google OAuth fastest)
3. Verify email
4. Navigate to Dashboard

### Step 2: Get API Key

In HeyGen Dashboard:

1. **Settings** → **API Keys**
2. **Create New API Key**
3. Copy key (starts with `sk_`)
4. Save securely

### Step 3: Choose or Create Avatar

**Option A: Use Default Avatar (Fastest)**

```bash
# No setup needed, use in code
HEYGEN_AVATAR_ID=default_male
HEYGEN_VOICE_ID=male_neutral
```

**Option B: Create Custom Avatar (2-4 hours)**

In HeyGen Dashboard:

1. **Avatars** → **Create Custom Avatar**
2. **Upload photo** (clear headshot)
3. **Wait for processing** (2-4 hours)
4. **Copy Avatar ID** when ready
5. Use in environment: `HEYGEN_AVATAR_ID=avatar_xxxxx`

**Option C: Clone Your Voice (Optional)**

1. **Voices** → **Create Custom Voice**
2. **Upload audio** (1-5 minute sample)
3. **Wait for processing** (2-4 hours)
4. **Copy Voice ID** when ready

### Step 4: Create Environment File

```bash
cd /home/r2d2/brain/agents/video
cat > .env << 'EOF'
HEYGEN_API_KEY=sk_your_api_key_here
HEYGEN_AVATAR_ID=default_male
HEYGEN_VOICE_ID=male_neutral
EOF

chmod 600 .env
```

### Step 5: Install Dependencies

```bash
cd /home/r2d2/brain/agents/video
pip install requests python-dotenv boto3
```

### Step 6: Test Video Generation

```bash
cd /home/r2d2/brain/agents/video
python3 video_agent.py
```

**Expected Output:**
```
📹 Video Generation Demo
==================================================

1️⃣ Generating video...
✅ Video ID: e8c69848
Status: processing

2️⃣ Listing all videos...
Total videos: 1

3️⃣ Scheduling batch videos...
✅ Scheduled: Video 2
✅ Scheduled: Video 3
```

### Step 7: Monitor Video Status

```bash
# Check video info
python3 -c "
from video_agent import VideoManager
manager = VideoManager()
info = manager.get_video_info('video_e8c69848')
print(f\"Status: {info['status']}\")
print(f\"Progress: {info.get('progress', 0)}%\")
"

# List all videos
python3 -c "
from video_agent import VideoManager
manager = VideoManager()
for v in manager.list_videos():
    print(f\"{v['title']}: {v['status']}\")
"

# Monitor metadata
cat /home/r2d2/brain/agents/video/metadata/video_*.json | jq '.status'
```

### Step 8: Download Completed Video

```bash
python3 -c "
from video_agent import VideoManager
manager = VideoManager()
video_path = manager.download_video('video_e8c69848')
print(f'Downloaded to: {video_path}')
"

# Check video exists
ls -lh /home/r2d2/videos/
```

### Step 9: Upload to YouTube (Optional)

```bash
# Install youtube-upload
pip install youtube-upload

# Upload video
youtube-upload --title='AI Agents Introduction' \
  --description='Learn about AI agents and autonomous systems' \
  /home/r2d2/videos/video_e8c69848.mp4
```

Or upload manually:
1. Go to youtube.com/studio
2. Click "Create" → "Upload videos"
3. Select video from `/home/r2d2/videos/`
4. Add title, description, tags
5. Publish

### ✅ Phase 3 Complete!

Video agent is ready for batch generation. Test with:

```bash
# Generate a new video
python3 -c "
from video_agent import VideoManager, VideoRequest
manager = VideoManager()
request = VideoRequest(
    script='Hello from Suhail! This is a test video.',
    title='Test Video',
    video_type='intro'
)
result = manager.generate_video(request)
print(f'✅ Generated: {result[\"video_id\"]}')
"

# Check status
ls /home/r2d2/videos/
```

---

## Integration Testing

### Test All Three Agents Together

```bash
# 1. Yoda generates a new guide
python3 /home/r2d2/brain/agents/yoda/yoda_learning_agent.py

# 2. Voice agent can discuss the guide
# Call: "Tell me about the new guides Yoda learned"

# 3. Video agent creates tutorial from guide
python3 -c "
from video_agent import VideoManager, VideoRequest
manager = VideoManager()
request = VideoRequest(
    script='New guide from Yoda on AI agents',
    title='AI Agents Tutorial',
    video_type='tutorial'
)
manager.generate_video(request)
"

# 4. Monitor all systems
echo '=== Yoda State ==='
cat /home/r2d2/brain/agents/yoda/learning_state.json | jq .

echo '=== Voice Calls ==='
cat /home/r2d2/brain/agents/voice/call_log.jsonl | tail -3 | jq .

echo '=== Video Status ==='
cat /home/r2d2/brain/agents/video/schedule.json | jq '.[] | {title, status}'
```

---

## Troubleshooting

### Yoda Issues

| Problem | Solution |
|---------|----------|
| Cron not running | `sudo service cron restart` |
| No logs created | Check directory exists: `mkdir -p /home/r2d2/.openclaw/workspace/memory` |
| Memory not updating | Verify MEMORY.md permissions: `chmod 666 MEMORY.md` |

### Voice Issues

| Problem | Solution |
|---------|----------|
| Webhook not receiving calls | Verify URL in Vapi dashboard matches |
| No response to voice | Check OpenAI API key validity |
| Transcription fails | Ensure Whisper is enabled in Vapi |
| Connection timeout | Check firewall rules: `sudo ufw allow 5000/tcp` |

### Video Issues

| Problem | Solution |
|---------|----------|
| Generation stuck | Check HeyGen API status page |
| Wrong avatar | Verify HEYGEN_AVATAR_ID in .env |
| No audio | Ensure HEYGEN_VOICE_ID is valid |
| Download fails | Check `/home/r2d2/videos/` has write permissions |

---

## Monitoring & Maintenance

### Daily Monitoring

```bash
#!/bin/bash
# daily-check.sh

echo "=== Yoda Status ==="
cat /home/r2d2/brain/agents/yoda/learning_state.json | jq '.last_learned'

echo "=== Voice Calls Today ==="
cat /home/r2d2/brain/agents/voice/call_log.jsonl | \
  grep "$(date +%Y-%m-%d)" | wc -l

echo "=== Video Processing ==="
find /home/r2d2/brain/agents/video/metadata -mtime -1 | wc -l

echo "=== Storage Usage ==="
du -sh /home/r2d2/brain/agents/
du -sh /home/r2d2/videos/
```

### Weekly Maintenance

```bash
# Archive old logs
find /home/r2d2/brain/agents/voice -name "*.jsonl" \
  -mtime +7 -exec gzip {} \;

# Review Yoda digest
cat /home/r2d2/brain/agents/yoda/digest_*.md

# Check storage limits
du -sh /home/r2d2/brain/agents/video/metadata/
```

---

## Rollback Plan

If any agent causes issues:

### Yoda Rollback

```bash
# Remove from crontab
crontab -e
# Delete 4 Yoda lines

# Verify removed
crontab -l | grep -c yoda  # Should return 0
```

### Voice Rollback

```bash
# Stop webhook
sudo systemctl stop voice-webhook

# Verify stopped
sudo systemctl status voice-webhook  # Should show inactive
```

### Video Rollback

```bash
# Disable video generation
rm /home/r2d2/brain/agents/video/.env

# Videos won't be generated until .env restored
```

---

## Success Criteria

### Yoda ✅
- [ ] Runs 4 times daily on schedule
- [ ] Creates new guides in `/home/r2d2/projects/yoda/knowledge/`
- [ ] Updates MEMORY.md with summaries
- [ ] Generates weekly digests (Mondays)

### Voice ✅
- [ ] Phone number answers calls
- [ ] Recognizes voice commands
- [ ] Creates tasks from voice input
- [ ] Reads daily briefing
- [ ] Saves voice memos

### Video ✅
- [ ] Generates videos to completion
- [ ] Videos store in `/home/r2d2/videos/`
- [ ] Scripts auto-generate
- [ ] Batch scheduling works
- [ ] Videos ready for YouTube

---

## Support

For issues or questions:

1. **Check README files:**
   - `/home/r2d2/brain/agents/yoda/README.md`
   - `/home/r2d2/brain/agents/voice/README.md`
   - `/home/r2d2/brain/agents/video/README.md`

2. **Check logs:**
   - Yoda: `/home/r2d2/.openclaw/workspace/memory/yoda_learning_*.log`
   - Voice: `/home/r2d2/brain/agents/voice/call_log.jsonl`
   - Video: `/home/r2d2/brain/agents/video/metadata/*.json`

3. **Test manually:**
   - Yoda: `python3 /home/r2d2/brain/agents/yoda/yoda_learning_agent.py`
   - Voice: Call phone number
   - Video: `python3 /home/r2d2/brain/agents/video/video_agent.py`

---

**Created:** 2026-03-20
**Updated:** 2026-03-20
**Status:** Ready for phased deployment
**Estimated Total Time:** 2-3 weeks
