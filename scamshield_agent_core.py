# “””
ScamShield Agent Core — Groq API Version

Main AI agent logic using Groq API (llama-3.3-70b-versatile).
“””

from groq import Groq
import json
import os
import re
from pathlib import Path

class ScamShieldAgent:

```
def __init__(self):
    self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    self.model = "llama-3.3-70b-versatile"
    self.vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"
    self.max_tokens = 800
    self.system_prompt = self._load_system_prompt()

def _load_system_prompt(self) -> str:
    prompt_file = Path(__file__).parent / "scamshield_agent_system_prompt.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    raise FileNotFoundError("System prompt file not found.")

def analyze_chat(self, chat_text: str, user_name: str = "there") -> dict:
    if len(chat_text.strip()) < 20:
        return {"error": "Chat too short. Please provide more conversation."}
    prompt = f"My name is {user_name}. Please analyze this suspicious chat:\n\n{chat_text[:3000]}"
    response = self.client.chat.completions.create(
        model=self.model,
        max_tokens=self.max_tokens,
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        raw = json_match.group(0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"conversational": True, "message": raw}

def ask_question(self, question: str, user_name: str = "there") -> str:
    response = self.client.chat.completions.create(
        model=self.model,
        max_tokens=500,
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"My name is {user_name}. {question}"}
        ]
    )
    return response.choices[0].message.content.strip()

def check_platform(self, platform_name: str, user_name: str = "there") -> str:
    prompt = f'My name is {user_name}. Someone wants me to invest through "{platform_name}". Is it legitimate or a scam?'
    response = self.client.chat.completions.create(
        model=self.model,
        max_tokens=500,
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def generate_interrogation_questions(self, scam_type: str, platform: str = None, user_name: str = "there") -> list:
    platform_str = f" Platform: {platform}." if platform else ""
    prompt = f'My name is {user_name}. I am dealing with a {scam_type} scam.{platform_str} Give me 7 questions to catch the scammer. Return as JSON array only: ["q1","q2",...]'
    response = self.client.chat.completions.create(
        model=self.model,
        max_tokens=400,
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    raw = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return [raw]

def get_regional_threat(self, city: str) -> str:
    response = self.client.chat.completions.create(
        model=self.model,
        max_tokens=400,
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"What scams are most active in {city}, UK right now?"}
        ]
    )
    return response.choices[0].message.content.strip()

def extract_text_from_image(self, base64_image: str, media_type: str = "image/jpeg") -> str:
    response = self.client.chat.completions.create(
        model=self.vision_model,
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Extract all text from this image exactly as it appears. This is likely a scam chat screenshot. Show who said what in order. Return only the extracted text."
                    }
                ]
            }
        ]
    )
    return response.choices[0].message.content.strip()
```