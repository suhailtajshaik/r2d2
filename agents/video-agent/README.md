# Video Agent - HeyGen Integration

**AI video generation with synthetic avatars and voice**

## Overview

Video Agent creates professional videos using HeyGen's AI avatar technology. You can generate:
- Personal video messages
- Educational videos
- Product demos
- YouTube content
- Marketing videos

## Status

**Current:** Ready for setup (code written, awaiting HeyGen account)
**Setup Time:** 2-3 days
**Complexity:** Medium

## Setup Requirements

### 1. Create HeyGen Account
- Go to https://heygen.com
- Sign up for API access
- Create a custom avatar (or use preset)
- Get API key

### 2. Configure Video Agent
```bash
cd /home/r2d2/brain/agents/video-agent
# Update config with your HeyGen API key
export HEYGEN_API_KEY=your_key_here
```

### 3. Create Avatar Script
- Choose avatar style (professional, casual, etc.)
- Record voice sample or use TTS
- Test with sample script

### 4. Deploy
```bash
docker build -t video-agent .
docker run -e HEYGEN_API_KEY=$HEYGEN_API_KEY video-agent
```

## Features (When Set Up)

### Quick Videos
```
You request: "Create a 30-second video introducing my SaaS"
Agent:
  - Generates script from your brief
  - Creates video with your avatar
  - Syncs voiceover
  - Returns MP4
```

### Use Cases

1. **Educational Content**
   - Tutorials
   - How-to guides
   - Technical explanations
   - Learning content from Yoda

2. **Product Demos**
   - Feature walkthroughs
   - Product launch videos
   - Update announcements
   - User onboarding

3. **Personal Content**
   - Video messages
   - Announcements
   - Briefings (audio → video)
   - Status updates

4. **YouTube Content**
   - Automated video generation
   - Batch processing
   - Playlist creation
   - Channel automation

## Architecture

```
Request: "Create video about [topic]"
  ↓
Generate script (Claude)
  ↓
HeyGen API call
  ↓
Create avatar video + voiceover
  ↓
Return MP4 file
  ↓
Upload to storage / YouTube
```

## Code Status

✅ **HeyGen API integration ready**
✅ **Script generation ready**
✅ **Video processing ready**
✅ **YouTube upload code ready**

⏳ **Awaiting:** HeyGen account creation

## Integration with Other Agents

### With Yoda
- Yoda creates learning guide
- Video Agent converts to video
- Publish to YouTube/website

### With Maxwell
- Maxwell generates report
- Video Agent creates summary video
- Share via email/Notion

### With 3PO
- 3PO writes code
- Video Agent creates tutorial
- Publish to docs site

## Features

### Video Types

**Tutorial Videos**
```
Input: "Create a 5-min tutorial on React hooks"
Output: Professional video with avatar explaining concepts
```

**Product Demos**
```
Input: "Demo the new dashboard feature"
Output: 3-min demo video with screen recording
```

**Status Updates**
```
Input: "Record weekly standup"
Output: 2-min team update video
```

**Learning Content**
```
Input: "Convert this guide to video"
Output: Narrated video with visuals
```

## Advanced Features

### Batch Processing
- Generate 10+ videos in parallel
- Different avatars per video
- A/B test messaging

### Customization
- Custom avatar appearance
- Voice selection
- Background/branding
- Watermarks

### Publishing
- Auto-upload to YouTube
- Email delivery
- Notion embedding
- Website embedding

## Future Enhancements

- [ ] Screen recording + avatar overlay
- [ ] Multi-avatar conversations
- [ ] Real-time video generation
- [ ] Lip-sync with custom audio
- [ ] Video editing and effects
- [ ] Analytics and engagement tracking
- [ ] A/B testing interface
- [ ] Template library

## Files

- `video_generator.py` — Main video creation
- `script_generator.py` — AI script writing
- `heygen_api.py` — HeyGen integration
- `youtube_uploader.py` — YouTube publishing
- `config.yaml` — Configuration
- `requirements.txt` — Dependencies
- `Dockerfile` — Container setup

## Next Steps

1. **Create HeyGen account** (https://heygen.com)
2. **Get API key**
3. **Create custom avatar** (or choose preset)
4. **Update config.yaml**
5. **Deploy container**
6. **Test video generation**

## Pricing

HeyGen pricing:
- Free tier: 1-3 videos/month
- Starter: $10/month (10 videos)
- Pro: $100/month (unlimited)

Recommendation: Start with Starter tier for testing.

---

**Created:** 2026-03-21
**Status:** Ready for HeyGen setup
**ETA to Production:** 2-3 days after HeyGen account created
