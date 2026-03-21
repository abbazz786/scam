"""
ScamShield Agent Core — Groq API Version
==========================================
Main AI agent logic using Groq API (llama-3.3-70b-versatile).
Fast, free tier available, production-ready.
"""

from groq import Groq
import json
import os
from pathlib import Path


class ScamShieldAgent:
    """
    Core ScamShield agent that analyzes chats and conversations
    for scam patterns using Groq API with full UK intelligence.
    """

    def __init__(self):
self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"        self.max_tokens = 1500
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        prompt_file = Path(__file__).parent / "scamshield_agent_system_prompt.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        raise FileNotFoundError("System prompt file not found.")

    def analyze_chat(self, chat_text: str, user_name: str = "there") -> dict:
        """Analyze a suspicious chat for scam patterns."""
        if len(chat_text.strip()) < 20:
            return {"error": "Chat too short. Please provide more conversation."}

        prompt = f"""My name is {user_name}. Please analyze this suspicious chat and provide your full assessment:

{chat_text[:8000]}"""

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        # Try to extract JSON block
        import re
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"conversational": True, "message": raw}

    def ask_question(self, question: str, user_name: str = "there") -> str:
        """Answer a conversational question about scams."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"My name is {user_name}. {question}"}
            ]
        )
        return response.choices[0].message.content.strip()

    def check_platform(self, platform_name: str, user_name: str = "there") -> str:
        """Check if a specific platform is legitimate or known scam vehicle."""
        prompt = f"""My name is {user_name}. Someone is asking me to invest through a platform called "{platform_name}".
Is this a legitimate FCA-regulated platform or is it known to be used by scammers?
What questions should I ask to verify it?"""

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    def generate_interrogation_questions(
        self, scam_type: str, platform: str = None, user_name: str = "there"
    ) -> list:
        """Generate targeted interrogation questions for a specific scam."""
        platform_str = f" They mentioned the platform: {platform}." if platform else ""
        prompt = f"""My name is {user_name}. I'm dealing with a {scam_type} scam.{platform_str}
Generate 7 smart questions I can ask the scammer to catch them in lies.
Return as JSON array only: ["question1", "question2", ...]"""

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return [raw]

    def get_regional_threat(self, city: str) -> str:
        """Get current scam threats for a specific UK city."""
        prompt = f"""What scams are currently most active in {city}, UK?
Who is most at risk and what should people watch out for right now?"""

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    def extract_text_from_image(self, base64_image: str, media_type: str = "image/jpeg") -> str:
        """
        Extract text from a screenshot or photo using Groq vision model.
        Used for reading scam conversations from images the user uploads.
        """
        response = self.client.chat.completions.create(
            model="llama-3.2-11b-vision-instruct",
            max_tokens=2000,
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
                            "text": (
                                "Extract all the text from this image exactly as it appears. "
                                "This is likely a screenshot of a chat conversation, SMS messages, "
                                "or an email. Preserve the conversation structure — show who said what, "
                                "in order. Include timestamps if visible. "
                                "Return only the extracted text. Do not add commentary or analysis."
                            )
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content.strip()
