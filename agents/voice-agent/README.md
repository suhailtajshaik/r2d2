# Voice Agent - Vapi Integration

**AI voice assistant for calls, voice commands, and audio briefings**

## Overview

Voice Agent enables you to interact with systems via voice calls. Through Vapi integration, you can:
- Make voice calls to get briefings
- Ask questions and receive spoken answers
- Create voice reminders and alerts
- Have conversations with your personal AI assistant

## Status

**Current:** Ready for setup (code written, awaiting Vapi account)
**Setup Time:** 3-5 days
**Complexity:** Medium

## Setup Requirements

### 1. Create Vapi Account
- Go to https://vapi.ai
- Sign up for free
- Create your first assistant
- Get API key

### 2. Configure Voice Agent
```bash
cd /home/r2d2/brain/agents/voice-agent
# Update config with your Vapi API key
export VAPI_API_KEY=your_key_here
```

### 3. Set Webhook URL
- Point Vapi to: `https://suhailtaj.cloud/voice-webhook/`
- Vapi will call this endpoint when incoming calls arrive

### 4. Deploy
```bash
docker build -t voice-agent .
docker run -e VAPI_API_KEY=$VAPI_API_KEY voice-agent
```

## Features (When Set Up)

### Incoming Calls
```
You call your Vapi number →
Agent answers →
You speak: "What's my schedule today?"
Agent: "You have 3 meetings: [lists them]"
```

### Voice Commands
- "Send a reminder to..."
- "What's the weather?"
- "Read me today's news"
- "Schedule a meeting for..."
- "What's on my calendar tomorrow?"

### Briefings
- Morning briefing (7 AM)
- News briefing (10 AM)
- End-of-day summary (6 PM)
- Weekly review (Mondays 9 AM)

### Integration Points
- Calendar (Google Calendar)
- Email (Gmail)
- News (Maxwell newspaper)
- Reminders (Notion)
- Tasks (TODO list)

## Architecture

```
Vapi Phone Line
  ↓
Your incoming call
  ↓
Vapi recognizes your number
  ↓
Webhook → /voice-webhook/
  ↓
Voice Agent processes request
  ↓
Generates spoken response
  ↓
Vapi returns audio to your call
```

## Code Status

✅ **Vapi webhook integration ready**
✅ **Voice response synthesis ready**
✅ **Calendar integration code ready**
✅ **News briefing code ready**

⏳ **Awaiting:** Vapi account creation

## Integration with Other Agents

### With Guardian
- "Is my infrastructure healthy?" → Guardian status
- "Any alerts?" → Guardian alerts
- "Restart [service]" → Guardian executes

### With Maxwell
- "What's today's news?" → Maxwell newspaper read aloud
- "Market summary?" → Maxwell market analysis

### With Yoda
- "What have I learned?" → Yoda learning digest
- "Any new guides?" → Yoda recent syntheses

## Future Features

- [ ] Natural language task creation
- [ ] Voice-to-text note taking
- [ ] Meeting transcription and summary
- [ ] Voice commands for infrastructure
- [ ] Emergency alert calls
- [ ] Daily standup recording
- [ ] Voice authentication (recognize your voice)

## Files

- `webhook_handler.py` — Incoming call handler
- `voice_synthesizer.py` — Text-to-speech
- `briefing_generator.py` — Creates briefings
- `config.yaml` — Configuration
- `requirements.txt` — Dependencies
- `Dockerfile` — Container setup

## Next Steps

1. **Create Vapi account** (https://vapi.ai)
2. **Get API key and phone number**
3. **Update config.yaml with API key**
4. **Configure webhook URL**
5. **Deploy container**
6. **Test with incoming call**

---

**Created:** 2026-03-21
**Status:** Ready for Vapi setup
**ETA to Production:** 3-5 days after Vapi account created
