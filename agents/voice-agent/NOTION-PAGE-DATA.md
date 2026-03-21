# Voice Agent - Notion Page Data

**Add to Notion immediately**

Parent: Agents (324c2d43-b275-8179-aeb3-c22edc04ee68)

## Properties

### Type
Webhook + Voice API

### Status
Ready for setup (awaiting Vapi account)

### Role
Voice interaction with AI assistant

### Description

Voice Agent enables you to interact via voice calls. Through Vapi integration, you can make calls to ask questions, get briefings, set reminders, and control systems via voice.

**Features:**
- Incoming voice calls
- Voice commands for tasks
- Daily briefings (morning, news, end-of-day)
- Calendar integration
- Task creation via voice
- Infrastructure control via voice

### Location
`/home/r2d2/brain/agents/voice-agent/`

### Setup Required

**Current Status:** Code ready, awaiting Vapi account

**To Deploy:**
1. Create account at https://vapi.ai
2. Get API key and phone number
3. Update config with key
4. Configure webhook URL
5. Deploy container

**Estimated Time:** 3-5 days

### Integration Points
- Calendar (Google Calendar)
- Email (Gmail)
- News (Maxwell newspaper)
- Infrastructure (Guardian)
- Learning (Yoda)
- Tasks (Notion)

### Key Files
- README.md — Setup instructions
- webhook_handler.py — Call handler
- voice_synthesizer.py — Text-to-speech
- config.yaml — Configuration
- requirements.txt — Dependencies

### Code Status
✅ Vapi webhook integration
✅ Voice response synthesis
✅ Calendar integration
✅ News briefing code
⏳ Awaiting Vapi account

### Future Features
- Natural language task creation
- Voice-to-text notes
- Meeting transcription
- Voice infrastructure control
- Emergency alert calls
- Voice authentication

### Created
2026-03-21

### Last Updated
2026-03-21

### Related Agents
- Maxwell — News briefings
- Guardian — Infrastructure alerts
- Yoda — Learning queries
