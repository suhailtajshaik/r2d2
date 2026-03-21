# Video Clone Agent (HeyGen Integration) 🎬

**Generate video content with AI avatar**

## Overview

The Video Agent uses HeyGen to automatically generate talking head videos with an AI avatar. Perfect for:
- Product/project announcements
- YouTube intros and tutorials
- Promotional content
- Project update videos
- Educational content

## Features

✅ **AI Avatar** - Professional talking head videos
✅ **Auto-Script Writing** - AI generates video scripts
✅ **Batch Generation** - Schedule multiple videos
✅ **Customizable** - Avatar style, voice, background
✅ **Direct to YouTube** - Videos ready to upload
✅ **CDN Ready** - Share via public links

## Architecture

```
video_agent.py                 # Main agent
├── VideoRequest               # Video generation request
├── ScriptWriter()            # AI script generation
├── HeyGenAPIClient()         # HeyGen API integration
├── VideoManager()            # Video lifecycle management
└── VideoScheduler()          # Batch scheduling

/home/r2d2/brain/agents/video/
├── videos/                    # Generated videos (.mp4)
├── scripts/                   # Video scripts (.txt)
├── metadata/                  # Video metadata (.json)
├── schedule.json             # Scheduled jobs
└── README.md

/home/r2d2/videos/            # Video output directory
├── video_abc123.mp4
├── video_def456.mp4
└── ...
```

## Setup

### 1. Sign Up for HeyGen

Go to https://heygen.com and create an account.

### 2. Get API Key

- Dashboard → Account Settings → API Keys
- Create new API key
- Copy and save securely

### 3. Choose or Create Avatar

**Option A: Default Avatar (Fastest)**
```
- Avatar ID: "default_male" or "default_female"
- Style: Professional, casual, or friendly
- No custom setup needed
```

**Option B: Custom Avatar (Advanced)**
```
- Upload your photo
- HeyGen will create AI avatar matching your likeness
- Takes 2-4 hours for processing
- Avatar ID: assigned by HeyGen
```

**Option C: Clone Your Voice (Advanced)**
```
- Upload 1-5 minute voice sample
- HeyGen clones your voice
- Sounds like you reading the script
```

### 4. Configure Environment

Create `.env` in `/home/r2d2/brain/agents/video/`:

```bash
HEYGEN_API_KEY=sk_your_heygen_api_key_here
HEYGEN_AVATAR_ID=default_male
HEYGEN_VOICE_ID=male_neutral
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=your-videos-bucket
```

### 5. Install Dependencies

```bash
cd /home/r2d2/brain/agents/video
pip install requests python-dotenv boto3
```

### 6. Test Setup

```bash
python3 video_agent.py
# Should output demo video generation info
```

## Usage

### Generate a Single Video

```python
from video_agent import VideoManager, VideoRequest

manager = VideoManager()

request = VideoRequest(
    script="Hello! Welcome to my channel. Today we're exploring AI agents.",
    title="AI Agents Introduction",
    video_type="intro",  # "intro", "announcement", "tutorial", "update"
    avatar_style="professional",  # "professional", "casual", "friendly"
    background="minimalist",  # "minimalist", "office", "studio"
    voice="male_neutral",
)

response = manager.generate_video(request)
print(f"Video ID: {response['video_id']}")
print(f"Status: {response['status']}")
# Output: Video processing... (takes 2-5 minutes)
```

### Generate from Script

```python
from video_agent import ScriptWriter, VideoManager, VideoRequest

writer = ScriptWriter()

# Write announcement script
script = writer.write_announcement_script(
    topic="Yoda Learning Agent Launch",
    key_points=[
        "Autonomous knowledge expansion",
        "Real-time trend monitoring",
        "Auto-synthesized guides"
    ]
)

# Save script
script_path = writer.save_script(script, "yoda_announcement")

# Generate video
manager = VideoManager()
request = VideoRequest(
    script=script,
    title="Yoda Learning Agent Announcement",
    video_type="announcement",
)
response = manager.generate_video(request)
```

### Schedule Multiple Videos

```python
from video_agent import VideoScheduler, VideoRequest

scheduler = VideoScheduler()

# Schedule videos for later
videos = [
    {
        "title": "Voice Agent Introduction",
        "type": "intro",
        "schedule": "2026-03-21 10:00:00"
    },
    {
        "title": "Video Agent Tutorial",
        "type": "tutorial",
        "schedule": "2026-03-22 14:00:00"
    },
]

for video in videos:
    request = VideoRequest(
        script=f"Video about {video['title']}",
        title=video['title'],
        video_type=video['type'],
    )
    job = scheduler.schedule_video(request, video['schedule'])
    print(f"✅ Scheduled: {job['id']}")

# Later, process all scheduled videos that are ready
scheduler.process_scheduled_videos()
```

### Download Completed Video

```python
manager = VideoManager()

# Check status
info = manager.get_video_info("video_abc123")
print(info['status'])  # "completed"

# Download
video_path = manager.download_video("video_abc123")
print(f"Downloaded to: {video_path}")
# /home/r2d2/videos/video_abc123.mp4
```

### List All Videos

```python
manager = VideoManager()

videos = manager.list_videos()
for v in videos:
    print(f"{v['title']} - {v['status']}")
    print(f"  Created: {v['created_at']}")
    print(f"  URL: {v.get('download_url', 'Processing...')}")
```

## Script Types

### Announcement Script

```python
script = writer.write_announcement_script(
    topic="New Feature Release",
    key_points=[
        "Feature 1 benefits",
        "Feature 2 benefits",
        "Feature 3 benefits"
    ]
)
```

Output:
```
ANNOUNCEMENT: New Feature Release

[INTRO - 5 seconds]
"Hey everyone! I'm excited to share something new with you."

[MAIN CONTENT - 30 seconds]
Point 1: Feature 1 benefits
Point 2: Feature 2 benefits
Point 3: Feature 3 benefits

[CTA - 5 seconds]
"Check it out and let me know what you think!"

[OUTRO - 3 seconds]
"Thanks for watching!"
```

### Tutorial Script

```python
script = writer.write_tutorial_script(
    topic="Set Up a Voice Agent",
    steps=[
        "Sign up for Vapi",
        "Create phone number",
        "Deploy webhook",
        "Test with a call"
    ]
)
```

### Intro Script

```python
script = writer.write_intro_script(
    name="Suhail",
    tagline="Building AI agents and autonomous systems"
)
```

## API Reference

### VideoRequest

```python
@dataclass
class VideoRequest:
    script: str                              # Video script
    title: str                               # Video title
    video_type: str                          # "intro", "announcement", "tutorial", "update"
    avatar_style: str = "professional"       # Avatar appearance
    background: str = "minimalist"           # Background scene
    voice: str = "male_neutral"              # Voice ID
    duration_estimate: Optional[int] = None  # Estimated seconds
```

### VideoManager Methods

```python
manager = VideoManager()

# Generate new video
response = manager.generate_video(request)
# → {"status": "processing", "video_id": "..."}

# Get video info
info = manager.get_video_info(video_id)
# → {"video_id": "...", "status": "completed", "download_url": "..."}

# Download completed video
path = manager.download_video(video_id)
# → /home/r2d2/videos/video_abc123.mp4

# List all videos
videos = manager.list_videos()
# → [{video1}, {video2}, ...]

# Delete video
success = manager.delete_video(video_id)
# → True
```

### VideoScheduler Methods

```python
scheduler = VideoScheduler()

# Schedule a video for later
job = scheduler.schedule_video(request, schedule_time="2026-03-21 10:00")
# → {"id": "...", "status": "scheduled"}

# Process all scheduled videos that are ready
results = scheduler.process_scheduled_videos()
# → [list of processed jobs]
```

## Monitoring Videos

### Check Status

```bash
# View all videos
python3 -c "
from video_agent import VideoManager
manager = VideoManager()
for v in manager.list_videos():
    print(f\"{v['title']}: {v['status']}\")
"
```

### Video Metadata

```bash
# View video info
cat /home/r2d2/brain/agents/video/metadata/video_abc123.json
```

### View Scheduled Jobs

```bash
cat /home/r2d2/brain/agents/video/schedule.json | jq .
```

## Upload to YouTube

Once your video is downloaded:

```bash
# Method 1: YouTube CLI (youtube-upload)
pip install youtube-upload
youtube-upload --title="AI Agents Introduction" \
  --description="Learn about AI agents..." \
  /home/r2d2/videos/video_abc123.mp4

# Method 2: Manual upload
# 1. Go to youtube.com/studio
# 2. Click "Create" → "Upload videos"
# 3. Select /home/r2d2/videos/video_abc123.mp4
# 4. Add title, description, tags
# 5. Publish
```

## Share via CDN

```bash
# Upload to S3 (requires AWS credentials)
python3 -c "
import boto3
s3 = boto3.client('s3')
s3.upload_file(
    '/home/r2d2/videos/video_abc123.mp4',
    'your-bucket',
    'videos/video_abc123.mp4',
    ExtraArgs={'ACL': 'public-read'}
)
print('https://your-bucket.s3.amazonaws.com/videos/video_abc123.mp4')
"
```

## Troubleshooting

### Video processing stuck

```bash
# Check HeyGen API status
curl https://api.heygen.com/v1/status

# Manually check video status
python3 -c "
from video_agent import VideoManager
manager = VideoManager()
info = manager.get_video_info('video_abc123')
print(info['status'])
"
```

### API key invalid

```bash
# Verify API key in HeyGen dashboard
# Settings → API Keys → Check key is active

# Test API key
export HEYGEN_API_KEY=sk_...
python3 -c "from video_agent import HeyGenAPIClient; c = HeyGenAPIClient(); print(c.list_avatars())"
```

### Video quality issues

1. **Check script length** - Aim for 30-60 seconds
2. **Check avatar selection** - Try different styles
3. **Check background** - "minimalist" works best for professional
4. **Check voice** - "male_neutral" is most reliable

## Pricing

- **HeyGen API:** $10-50/month for API access + per-minute video generation
- **TTS (ElevenLabs):** Included in HeyGen or $0.50/10K characters
- **AWS S3 (optional):** ~$0.023 per GB stored

## Batch Generation Example

```python
from video_agent import VideoManager, ScriptWriter, VideoRequest
import json

writer = ScriptWriter()
manager = VideoManager()

# Define batch of videos
batch = [
    {
        "title": "Yoda Learning Agent",
        "type": "announcement",
        "points": ["Gap detection", "Auto-research", "Weekly digest"]
    },
    {
        "title": "Voice Agent",
        "type": "introduction",
        "points": ["24/7 availability", "Task creation", "Daily briefing"]
    },
    {
        "title": "Video Agent",
        "type": "tutorial",
        "points": ["Script writing", "Avatar generation", "Direct to YouTube"]
    }
]

# Generate all
for video_config in batch:
    if video_config["type"] == "announcement":
        script = writer.write_announcement_script(
            topic=video_config["title"],
            key_points=video_config["points"]
        )
    else:
        script = f"Video about {video_config['title']}"
    
    request = VideoRequest(
        script=script,
        title=video_config["title"],
        video_type=video_config["type"]
    )
    
    response = manager.generate_video(request)
    print(f"✅ {response['video_id']}: {response['status']}")
```

## Integration with Other Agents

### Yoda → Video

```python
# Yoda generates guide → Video agent creates tutorial
from yoda_learning_agent import YodaLearningAgent
from video_agent import VideoManager

yoda = YodaLearningAgent()
manager = VideoManager()

# When Yoda creates a guide, also create video
for guide in yoda.knowledge_dir.glob("*.md"):
    topic = guide.stem.replace("_", " ").title()
    request = VideoRequest(
        script=f"Tutorial: {topic}",
        title=f"How to {topic}",
        video_type="tutorial"
    )
    manager.generate_video(request)
```

## Future Enhancements

- [ ] Voice cloning (your own voice)
- [ ] Custom avatars (your likeness)
- [ ] Automatic YouTube upload
- [ ] Caption generation
- [ ] Multi-language support
- [ ] Template library
- [ ] Analytics integration
- [ ] Webhook webhooks for completion events

## Related Agents

- **Yoda** - Create videos from learning guides
- **Voice** - Record video ideas via voice memo
- **Maxwell** - Schedule video generation with tasks

---

**Created:** 2026-03-20
**Last Updated:** 2026-03-20
**Status:** Ready for HeyGen Setup & Testing
**Output Directory:** `/home/r2d2/videos/`
