# Voice Agent (Vapi Integration) 📞

**Personal voice AI assistant available 24/7**

## Overview

The Voice Agent is a phone-accessible AI assistant powered by Vapi that lets Suhail:
- Create tasks via voice commands
- Check status of projects and tasks
- Get daily briefings read out loud
- Create voice memos that become tasks
- Ask quick questions without typing

## Features

✅ **Voice-to-Task** - "Create a task to..."
✅ **Status Checks** - "What's the status of X?"
✅ **Daily Briefing** - Morning summary via TTS
✅ **Voice Memos** - Record thoughts → auto-transcribe → task
✅ **24/7 Availability** - Call anytime from your phone
✅ **Context Aware** - Accesses MEMORY.md and task history

## Architecture

```
voice_agent_webhook.py        # Main webhook server
├── VoiceAgentWebhook()       # Receives Vapi calls
├── VoiceIntentProcessor()    # Processes voice intents
└── VoiceContextSystem()      # Pulls context from files

voice_context_system.py       # Context retrieval (planned)
voice_agent_cli.py            # Local testing CLI (planned)

/home/r2d2/brain/agents/voice/
├── call_log.jsonl            # All incoming calls (logged)
├── memos/                     # Voice memos (transcribed)
├── tasks.json                 # Task list (synced from projects)
└── state.json                 # Agent state
```

## Setup

### 1. Sign Up for Vapi

Go to https://vapi.ai and create an account.

### 2. Create Phone Number

- Purchase a phone number from Vapi (costs ~$10-20/month)
- Example: +1 (XXX) XXX-XXXX
- Note the number ID and phone number

### 3. Configure Voice Settings

In Vapi dashboard:

- **Model:** OpenAI GPT-4
- **TTS (Text-to-Speech):** ElevenLabs
- **Voice:** Male Neutral (or your preference)
- **Language:** English (US)

### 4. Deploy Webhook Endpoint

Set up the webhook endpoint where Vapi sends call events:

```
https://your-domain.com/voice-webhook
```

For development (ngrok tunneling):

```bash
# Install ngrok
brew install ngrok  # or download from ngrok.com

# Start tunnel to local Flask server (port 5000)
ngrok http 5000
# Output: https://xxxx-xx-xxx-xxx-xx.ngrok.io

# Use this URL in Vapi dashboard:
# https://xxxx-xx-xxx-xxx-xx.ngrok.io/voice-webhook
```

### 5. Set Vapi Webhook in Dashboard

- Go to Dashboard → Settings → Webhooks
- **Endpoint:** `https://your-domain.com/voice-webhook`
- **Events:** `call.started`, `call.ended`
- **Secret:** Copy and save (use for verification)

### 6. Environment Variables

Create `.env` in `/home/r2d2/brain/agents/voice/`:

```bash
VAPI_API_KEY=sk_your_vapi_api_key_here
VAPI_PHONE_ID=your_phone_id_here
VAPI_WEBHOOK_SECRET=your_webhook_secret_here
OPENAI_API_KEY=sk_your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

### 7. Deploy Webhook Server

Option A: **Local Development** (for testing)

```bash
cd /home/r2d2/brain/agents/voice
python3 -m pip install flask python-dotenv requests
python3 -m flask run --port 5000
```

Option B: **Production on OpenClaw**

```bash
# Start as background service
nohup python3 voice_webhook_server.py > webhook.log 2>&1 &

# Or with systemd:
sudo systemctl enable voice-webhook
sudo systemctl start voice-webhook
```

Option C: **Docker (Optional)**

```bash
docker build -t voice-agent .
docker run -e VAPI_API_KEY=... -p 5000:5000 voice-agent
```

## Usage

### Calling the Voice Agent

1. **Get the phone number** from Vapi dashboard
2. **Call it from your phone:** +1 (XXX) XXX-XXXX
3. **Speak naturally:**
   - "Create a task to review the video agent code"
   - "What's the status of the Yoda agent?"
   - "Give me my daily briefing"
   - "Record a memo: remember to check email"

### Testing Locally

```bash
cd /home/r2d2/brain/agents/voice

# Test the webhook handler
python3 -c "
from voice_agent_webhook import VoiceAgentWebhook

webhook = VoiceAgentWebhook()
test_request = {
    'event': 'call.ended',
    'call': {
        'id': 'test_001',
        'phoneNumber': '+14699941765',
        'startedAt': '2026-03-20T21:54:00Z',
        'messages': [
            {'role': 'user', 'content': 'Create a task to test the voice agent'}
        ]
    }
}

response = webhook.handle_webhook(test_request)
print(response)
"
```

### Monitoring Calls

```bash
# View all incoming calls
tail -f /home/r2d2/brain/agents/voice/call_log.jsonl

# View today's calls
cat /home/r2d2/brain/agents/voice/call_log.jsonl | \
  grep "$(date +%Y-%m-%d)" | jq .

# Count calls
wc -l /home/r2d2/brain/agents/voice/call_log.jsonl
```

### Voice Memos

Voice memos are automatically transcribed and stored:

```bash
ls /home/r2d2/brain/agents/voice/memos/
# Output: abc123.json, def456.json, ...

cat /home/r2d2/brain/agents/voice/memos/abc123.json
# {
#   "id": "abc123",
#   "timestamp": "2026-03-20T21:54:00Z",
#   "transcript": "Remember to review the video agent code...",
#   "phone": "+14699941765",
#   "converted_to_task": false
# }
```

## Intent Types

| Intent | Example | Action |
|--------|---------|--------|
| `task_create` | "Create a task to..." | Creates task in task list |
| `status_check` | "What's the status of...?" | Returns task status |
| `briefing` | "Give me my briefing" | Reads daily summary via TTS |
| `memo` | "Record a memo: ..." | Saves transcription → creates task |
| `general` | "How do I...?" | Escalates to human or searches |

## API Endpoints

### `/voice-webhook` (POST)

Receives call events from Vapi:

```bash
curl -X POST https://your-domain.com/voice-webhook \
  -H "Content-Type: application/json" \
  -H "X-Vapi-Signature: sha256=..." \
  -d '{
    "event": "call.ended",
    "call": {
      "id": "call_xyz",
      "phoneNumber": "+1234567890",
      "startedAt": "2026-03-20T21:54:00Z",
      "messages": [...]
    }
  }'
```

Response:

```json
{
  "status": "processed",
  "call_id": "call_xyz",
  "intent": "task_create",
  "response": "Task created!"
}
```

## File Structure

```
/home/r2d2/brain/agents/voice/
├── voice_agent_webhook.py          # Main webhook server
├── voice_context_system.py         # Context retrieval (TBD)
├── voice_agent_cli.py              # Local testing CLI (TBD)
├── .env                            # API keys (DO NOT commit)
├── .gitignore                      # Exclude .env
├── call_log.jsonl                  # All call history
├── state.json                      # Agent state
├── tasks.json                      # Synced task list
├── memos/                          # Voice memos (transcribed)
│   ├── abc123.json
│   └── def456.json
└── README.md                       # This file
```

## Integration Points

### Tasks
Reads from: `/home/r2d2/brain/agents/voice/tasks.json`
Source: Synced from projects/tasks

### Memory/Context
Reads from: `/home/r2d2/.openclaw/workspace/MEMORY.md`
Uses for: Briefings, status checks, context

### TTS Output
Voice: ElevenLabs (configured in Vapi)
Language: English (US)
Speed: Normal

### Transcription
Via: Vapi (includes OpenAI Whisper)
Format: JSON (timestamp + transcript + phone)

## Troubleshooting

### Webhook not receiving calls

1. **Check URL is correct:**
   ```bash
   curl https://your-domain.com/voice-webhook
   # Should return 405 (Method Not Allowed) for GET
   ```

2. **Verify Vapi dashboard webhook:**
   - Settings → Webhooks → Check URL and status
   - Should show "Active"

3. **Check firewall/networking:**
   ```bash
   # If using ngrok
   ngrok logs
   
   # Check webhook logs
   tail -f /var/log/voice-webhook.log
   ```

### Voice not being read

1. **Check TTS configuration in Vapi:**
   - Provider: ElevenLabs
   - Voice ID: Valid voice ID

2. **Test TTS directly:**
   ```python
   from elevenlabs import ElevenLabs
   client = ElevenLabs(api_key="...")
   audio = client.generate(text="Hello", voice_id="...")
   ```

### Transcription not working

1. **Check Whisper settings in Vapi**
2. **Verify audio quality** - clear speech works best
3. **Check language setting** - should be English (US)

### Webhook signature verification failing

```python
# Verify your webhook secret matches Vapi dashboard
import os
secret = os.getenv("VAPI_WEBHOOK_SECRET")
print(f"Secret: {secret}")
# Should match Vapi dashboard value
```

## Monitoring & Analytics

### Daily Metrics

```bash
# Calls today
cat /home/r2d2/brain/agents/voice/call_log.jsonl | \
  grep "$(date +%Y-%m-%d)" | wc -l

# Most common intents
cat /home/r2d2/brain/agents/voice/call_log.jsonl | \
  jq -r '.intent' | sort | uniq -c
```

### Cost Tracking

- **Phone number:** ~$10-20/month
- **TTS (ElevenLabs):** ~$0.50 per 10K characters
- **Transcription (Whisper):** Included in Vapi pricing

## Future Enhancements

- [ ] Slack/Discord notifications of voice memos
- [ ] Automatic task assignment based on context
- [ ] Multi-language support
- [ ] Call recording (opt-in)
- [ ] Custom voice cloning (Suhail's voice)
- [ ] Integration with calendar for smart scheduling
- [ ] Sentiment analysis of calls
- [ ] A/B testing different voices/responses

## Related Agents

- **Yoda** - Voice agent can query for learnings
- **Video** - Could generate videos from voice memos
- **Maxwell** - Main task/project management

---

**Created:** 2026-03-20
**Last Updated:** 2026-03-20
**Status:** Ready for Vapi Setup & Deployment
**Phone Number:** [TBD - from Vapi dashboard]
