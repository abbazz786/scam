from groq import Groq
import json
import os
import re
from pathlib import Path


class ScamShieldAgent:

    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.max_tokens = 500
        self._full_prompt = None
        self._core_prompt = None

    def _load_full_prompt(self):
        if self._full_prompt is None:
            p = Path(__file__).parent / "scamshield_agent_system_prompt.txt"
            if p.exists():
                self._full_prompt = p.read_text(encoding="utf-8")
            else:
                raise FileNotFoundError("System prompt file not found.")
        return self._full_prompt

    def _load_core_prompt(self):
        if self._core_prompt is None:
            self._core_prompt = self._load_full_prompt()
        return self._core_prompt

    def analyze_chat(self, chat_text, user_name="there"):
        if len(chat_text.strip()) < 20:
            return {"error": "Chat too short. Please provide more conversation."}
        prompt = "Analyze this suspicious message and return JSON only:\n\n" + chat_text[:2000]
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": self._load_core_prompt()},
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
            ai = json.loads(raw)
        except json.JSONDecodeError:
            return {"conversational": True, "message": raw}

        # Map AI response to display format
        score = int(ai.get("riskScore", 50))
        verdict = ai.get("verdict", "UNVERIFIED")
        risk_level = "DANGER" if score >= 70 else "WARNING" if score >= 40 else "SAFE"

        flags = []
        for f in ai.get("redFlags", []):
            flags.append({"title": f, "description": "", "severity": "high" if score >= 70 else "medium", "quote": ""})

        advice = []
        rec = ai.get("recommendation", "")
        if rec:
            advice = [s.strip() for s in rec.replace("\n", ".").split(".") if len(s.strip()) > 10][:4]

        report_to = ai.get("reportTo", "Report Fraud: reporting.reportfraud.police.uk")
        reporting_links = [{"name": "Report Fraud — City of London Police", "url": "https://reporting.reportfraud.police.uk/", "reason": report_to, "priority": "high"}]
        if score >= 70:
            reporting_links.append({"name": "Call 159 — Bank Fraud Hotline", "url": "https://www.stopscamsuk.org.uk/159", "reason": "Contact your bank immediately if money was involved", "priority": "high"})

        return {
            "verdict": verdict,
            "riskScore": score,
            "riskLevel": risk_level,
            "scamType": verdict,
            "personalizedSummary": ai.get("summary", ""),
            "flags": flags,
            "interrogationQuestions": [],
            "advice": advice,
            "reportingLinks": reporting_links,
            "victimSupportMessage": "You are not alone. Thousands of people are targeted by scams every day in the UK." if score >= 70 else "",
            "offerToDraft": ""
        }

    def ask_question(self, question, user_name="there"):
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=600,
            messages=[
                {"role": "system", "content": self._load_core_prompt()},
                {"role": "user", "content": "My name is " + user_name + ". " + question[:1500]}
            ]
        )
        return response.choices[0].message.content.strip()

    def check_platform(self, platform_name, user_name="there"):
        prompt = "My name is " + user_name + ". Someone wants me to invest through " + platform_name + ". Is it legitimate or a scam?"
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {"role": "system", "content": self._load_core_prompt()},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    def generate_interrogation_questions(self, scam_type, platform=None, user_name="there"):
        platform_str = " Platform: " + platform + "." if platform else ""
        prompt = "My name is " + user_name + ". I am dealing with a " + scam_type + " scam." + platform_str + " Give me 7 questions to catch the scammer. Return as JSON array only."
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=400,
            messages=[
                {"role": "system", "content": self._load_core_prompt()},
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return [raw]

    def get_regional_threat(self, city):
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=400,
            messages=[
                {"role": "system", "content": self._load_core_prompt()},
                {"role": "user", "content": "What scams are most active in " + city + ", UK right now?"}
            ]
        )
        return response.choices[0].message.content.strip()

    def extract_text_from_image(self, base64_image, media_type="image/jpeg"):
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
                                "url": "data:" + media_type + ";base64," + base64_image
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
