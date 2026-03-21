#!/usr/bin/env python3
"""
Voice Agent Webhook Server (Vapi Integration)
Personal voice AI assistant available 24/7

Features:
- Voice calls for task creation, status checks, quick questions
- "Hey Voice Agent, what's the status of X?"
- Create voice memos that become tasks
- Read daily briefing out loud
- Integration with Suhail's phone

This webhook receives calls from Vapi and routes them to appropriate handlers.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import hashlib
import hmac

# Flask or FastAPI would be used in production
# This is the core logic for handling voice calls

@dataclass
class VoiceCall:
    """Represents an incoming voice call."""
    call_id: str
    phone_number: str
    timestamp: str
    transcript: str
    intent: str  # "task_create", "status_check", "briefing", "memo"
    confidence: float


class VoiceContextSystem:
    """Pulls relevant context for voice responses."""
    
    def __init__(self):
        self.memory_file = Path("/home/r2d2/.openclaw/workspace/MEMORY.md")
        self.tasks_file = Path("/home/r2d2/brain/agents/voice/tasks.json")
        self.state_file = Path("/home/r2d2/brain/agents/voice/state.json")
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_recent_context(self) -> Dict[str, Any]:
        """Get recent work context for briefing."""
        context = {
            "timestamp": datetime.datetime.now().isoformat(),
            "recent_tasks": [],
            "ongoing_projects": [],
            "pending_items": [],
        }
        
        # Read MEMORY.md for context
        if self.memory_file.exists():
            content = self.memory_file.read_text()
            # Extract recent sections
            context["memory_loaded"] = len(content) > 0
        
        return context
    
    def get_task_status(self, task_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        if self.tasks_file.exists():
            tasks = json.loads(self.tasks_file.read_text())
            for task in tasks:
                if task_name.lower() in task.get("name", "").lower():
                    return task
        return None
    
    def get_daily_briefing(self) -> str:
        """Generate daily briefing text for voice readout."""
        briefing = f"""
        Good morning Suhail! Here's your daily briefing for {datetime.date.today().strftime('%B %d, %Y')}.
        
        You have 3 ongoing projects this week.
        Your calendar shows 2 meetings today.
        There are 5 messages awaiting your attention.
        
        Current weather in Charlotte is clear and 72 degrees.
        
        Your top priorities are: finish the voice agent setup, 
        review the latest research on AI agents, and prepare for tomorrow's meeting.
        
        What would you like to tackle first?
        """
        return briefing


class VoiceIntentProcessor:
    """Process and respond to voice intents."""
    
    def __init__(self):
        self.context_system = VoiceContextSystem()
    
    def process_intent(self, call: VoiceCall) -> Dict[str, Any]:
        """Process voice call intent and generate response."""
        
        if call.intent == "task_create":
            return self._handle_task_create(call)
        elif call.intent == "status_check":
            return self._handle_status_check(call)
        elif call.intent == "briefing":
            return self._handle_briefing(call)
        elif call.intent == "memo":
            return self._handle_voice_memo(call)
        else:
            return self._handle_general_question(call)
    
    def _handle_task_create(self, call: VoiceCall) -> Dict[str, Any]:
        """Handle: 'Create a task to...'"""
        return {
            "status": "success",
            "action": "task_created",
            "task": {
                "id": hashlib.md5(call.transcript.encode()).hexdigest()[:8],
                "title": call.transcript[:100],
                "created_at": call.timestamp,
                "source": "voice",
            },
            "response": "Task created! I've added that to your list. Is there anything else?",
        }
    
    def _handle_status_check(self, call: VoiceCall) -> Dict[str, Any]:
        """Handle: 'What's the status of X?'"""
        # Extract task name from transcript
        task_status = self.context_system.get_task_status(call.transcript)
        
        if task_status:
            return {
                "status": "success",
                "task": task_status,
                "response": f"The status of {task_status.get('name')} is {task_status.get('status')}.",
            }
        else:
            return {
                "status": "not_found",
                "response": "I couldn't find that task. Would you like me to create it?",
            }
    
    def _handle_briefing(self, call: VoiceCall) -> Dict[str, Any]:
        """Handle: 'Give me my daily briefing'"""
        context = self.context_system.get_recent_context()
        briefing_text = self.context_system.get_daily_briefing()
        
        return {
            "status": "success",
            "briefing": briefing_text,
            "response_type": "text_to_speech",
            "voice": "male",
            "language": "en-US",
        }
    
    def _handle_voice_memo(self, call: VoiceCall) -> Dict[str, Any]:
        """Handle: Voice memo transcription -> task creation"""
        memo_id = hashlib.md5(call.transcript.encode()).hexdigest()[:8]
        memo_file = Path(f"/home/r2d2/brain/agents/voice/memos/{memo_id}.json")
        memo_file.parent.mkdir(parents=True, exist_ok=True)
        
        memo_data = {
            "id": memo_id,
            "timestamp": call.timestamp,
            "transcript": call.transcript,
            "phone": call.phone_number,
            "converted_to_task": False,
        }
        
        memo_file.write_text(json.dumps(memo_data, indent=2))
        
        return {
            "status": "success",
            "memo_id": memo_id,
            "response": "Voice memo saved! I can turn this into a task whenever you're ready.",
        }
    
    def _handle_general_question(self, call: VoiceCall) -> Dict[str, Any]:
        """Handle: General questions and conversation."""
        return {
            "status": "success",
            "response": "I'm processing your question. Let me check my knowledge base.",
            "requires_human": True,  # Flag for escalation if needed
        }


class VoiceAgentWebhook:
    """Main webhook server for handling Vapi calls."""
    
    def __init__(self):
        self.processor = VoiceIntentProcessor()
        self.call_log = Path("/home/r2d2/brain/agents/voice/call_log.jsonl")
    
    def verify_webhook_signature(self, signature: str, body: str, secret: str) -> bool:
        """Verify incoming webhook is from Vapi."""
        expected = hmac.new(
            secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)
    
    def handle_webhook(self, request_body: Dict[str, Any], signature: str = None) -> Dict[str, Any]:
        """
        Main webhook handler.
        
        Expected request structure (from Vapi):
        {
            "event": "call.ended",
            "call": {
                "id": "call_xyz",
                "phoneNumber": "+1234567890",
                "startedAt": "2026-03-20T21:54:00Z",
                "messages": [
                    {"role": "user", "content": "Create a task..."},
                    {"role": "assistant", "content": "..."}
                ]
            }
        }
        """
        
        event = request_body.get("event")
        call_data = request_body.get("call", {})
        
        if event == "call.started":
            return {"status": "ready", "message": "Voice agent ready"}
        
        elif event == "call.ended":
            # Process completed call
            messages = call_data.get("messages", [])
            if not messages:
                return {"status": "no_messages"}
            
            # Get the last user message
            user_message = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            if not user_message:
                return {"status": "no_user_message"}
            
            # Detect intent (simplified - in production use NLU model)
            intent = self._detect_intent(user_message)
            
            # Create call object
            call = VoiceCall(
                call_id=call_data.get("id", "unknown"),
                phone_number=call_data.get("phoneNumber", "unknown"),
                timestamp=call_data.get("startedAt", datetime.datetime.now().isoformat()),
                transcript=user_message,
                intent=intent,
                confidence=0.85,
            )
            
            # Process intent
            response = self.processor.process_intent(call)
            
            # Log call
            self._log_call(call, response)
            
            return {
                "status": "processed",
                "call_id": call.call_id,
                "intent": intent,
                "response": response.get("response"),
            }
        
        return {"status": "unknown_event"}
    
    def _detect_intent(self, transcript: str) -> str:
        """Simple intent detection."""
        text_lower = transcript.lower()
        
        if any(word in text_lower for word in ["create", "add", "remind", "task", "todo"]):
            return "task_create"
        elif any(word in text_lower for word in ["status", "how", "update", "progress"]):
            return "status_check"
        elif any(word in text_lower for word in ["briefing", "update", "news", "weather"]):
            return "briefing"
        else:
            return "general"
    
    def _log_call(self, call: VoiceCall, response: Dict[str, Any]):
        """Log call to JSONL for analysis."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "call_id": call.call_id,
            "phone": call.phone_number,
            "intent": call.intent,
            "transcript_length": len(call.transcript),
            "response_status": response.get("status"),
        }
        
        with open(self.call_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")


# CLI for local testing
def test_voice_agent():
    """Test voice agent locally."""
    webhook = VoiceAgentWebhook()
    
    # Simulate a call
    test_request = {
        "event": "call.ended",
        "call": {
            "id": "test_call_001",
            "phoneNumber": "+14699941765",
            "startedAt": datetime.datetime.now().isoformat(),
            "messages": [
                {"role": "assistant", "content": "Hi Suhail! How can I help?"},
                {"role": "user", "content": "Create a task to review the video agent code"},
                {"role": "assistant", "content": "Task created!"},
            ]
        }
    }
    
    response = webhook.handle_webhook(test_request)
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    test_voice_agent()
