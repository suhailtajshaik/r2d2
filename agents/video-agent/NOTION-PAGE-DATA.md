# Video Agent - Notion Page Data

**Add to Notion immediately**

Parent: Agents (324c2d43-b275-8179-aeb3-c22edc04ee68)

## Properties

### Type
API Wrapper + Scheduler

### Status
Ready for setup (awaiting HeyGen account)

### Role
AI video generation with synthetic avatars

### Description

Video Agent creates professional videos using HeyGen's AI avatar technology.

**Video Types:**
- Educational tutorials
- Product demos
- Personal messages
- YouTube content
- Status updates
- Learning content (from Yoda)

### Location
`/home/r2d2/brain/agents/video-agent/`

### Setup Required

**Current Status:** Code ready, awaiting HeyGen account

**To Deploy:**
1. Create account at https://heygen.com
2. Get API key
3. Create custom avatar (or choose preset)
4. Update config with key
5. Deploy container

**Estimated Time:** 2-3 days

### Features
- Tutorial video generation
- Product demo videos
- Personal video messages
- YouTube content creation
- Batch processing (10+ videos in parallel)
- Custom avatars and voices
- Auto-upload to YouTube

### Use Cases
- Convert learning guides to videos
- Create product demos
- Generate YouTube content
- Record team updates
- Tutorial creation
- Knowledge sharing

### Integration Points
- Yoda (learning guides → videos)
- Maxwell (reports → summary videos)
- 3PO (code → tutorial videos)
- YouTube (auto-publishing)

### Key Files
- README.md — Setup and usage
- video_generator.py — Video creation
- script_generator.py — AI script writing
- heygen_api.py — HeyGen integration
- youtube_uploader.py — Publishing
- config.yaml — Configuration

### Code Status
✅ HeyGen API integration
✅ Script generation
✅ Video processing
✅ YouTube upload
⏳ Awaiting HeyGen account

### Pricing
- Free: 1-3 videos/month
- Starter: $10/month (10 videos)
- Pro: $100/month (unlimited)

### Created
2026-03-21

### Last Updated
2026-03-21

### Related Agents
- Yoda — Content source
- Maxwell — Reporting
- 3PO — Tutorial source
