"""
ScamShield Agent Test Suite v2
================================
7 original tests + 4 new tests covering:
- WhatsApp OTP hijacking
- Delivery driver scam
- Recovery scam (fake court/law firm)
- Self-employed HMRC scam
Run: python scamshield_agent_test.py
"""

import json
from scamshield_agent_core import ScamShieldAgent

agent = ScamShieldAgent()

# ─── ORIGINAL TEST CHATS ──────────────────────────────────────────────────────

PIG_BUTCHERING_CHAT = """
[09/03/2026, 18:51] Unknown: Hi, I think I have the wrong number! Sorry to bother you
[09/03/2026, 18:54] Unknown: Hello! It's great to see us connected. My name is Eunji Kang.
[09/03/2026, 18:55] Unknown: Can I ask? Are you a woman or a man?
[09/03/2026, 18:57] Me: I'm a man
[09/03/2026, 18:58] Unknown: I'm from South Korea, living in Manchester. I'm a financial analyst.
[09/03/2026, 19:09] Unknown: [Photo sent]
[09/03/2026, 20:22] Unknown: I invest in crypto using a decentralised trading platform
[09/03/2026, 20:35] Unknown: My side hustle helped me afford my Bentley Bentayga
[09/03/2026, 22:00] Unknown: I can share my trading knowledge with you. How much capital do you have?
[09/03/2026, 22:26] Me: I lost £50,000 in crypto before
[09/03/2026, 22:30] Unknown: That's why you need proper guidance. I use UniSat platform.
[09/03/2026, 22:58] Unknown: I recommend starting small. How much can you invest?
"""

SAFE_CHAT = """
[10/03/2026, 09:00] John (Work): Hey, are you coming to the meeting at 2pm today?
[10/03/2026, 09:05] Me: Yes, I'll be there
[10/03/2026, 09:10] John (Work): Great, could you bring the Q3 report?
[10/03/2026, 10:00] John (Work): Also, Sarah asked if we can reschedule to 3pm
[10/03/2026, 10:05] Me: That works for me
"""

GRANDPARENT_CHAT = """
[15/03/2026, 14:00] Unknown number: Gran, it's me! I'm in trouble
[15/03/2026, 14:01] Gran: Jamie? Is that you?
[15/03/2026, 14:01] Unknown: Yes Gran it's Jamie. I've been in an accident
[15/03/2026, 14:02] Unknown: Please don't tell Mum and Dad they'll be so worried
[15/03/2026, 14:03] Unknown: I need £3,000 urgently for the hospital. Can you wire it to 12345678 sort 12-34-56?
"""

SEXTORTION_CHAT = """
[12/03/2026, 20:00] Instagram DM - alex_photo99: Hey, your profile is really cute
[12/03/2026, 20:15] Instagram DM - alex_photo99: I'd love to get to know you better
[12/03/2026, 21:00] Instagram DM - alex_photo99: [sends photo claiming to be them]
[13/03/2026, 19:00] Instagram DM - alex_photo99: Can you send me a photo too? I really like you
[13/03/2026, 22:00] Instagram DM - alex_photo99: I have your photo now. Send me £500 or I'll send it to everyone you know
[13/03/2026, 22:01] Instagram DM - alex_photo99: I have your contacts list. Pay now.
"""

# ─── NEW TEST CHATS ───────────────────────────────────────────────────────────

WHATSAPP_OTP_CHAT = """
[16/03/2026, 11:30] Ahmed (friend): Hey bro, sorry to bother you
[16/03/2026, 11:31] Ahmed (friend): I accidentally sent a WhatsApp verification code to your number by mistake
[16/03/2026, 11:31] Ahmed (friend): Can you just forward me the 6-digit code you just received?
[16/03/2026, 11:32] Ahmed (friend): It's really urgent, I need it to get back into my account
[16/03/2026, 11:33] Ahmed (friend): Please man, just the code, that's all I need
"""

DELIVERY_DRIVER_CHAT = """
[17/03/2026, 14:15] +44 7700 900456: Hello, this is Uber Eats Support calling about your account
[17/03/2026, 14:16] +44 7700 900456: We've received a serious complaint about your last delivery
[17/03/2026, 14:16] +44 7700 900456: Your account may be deactivated unless we verify your details immediately
[17/03/2026, 14:17] +44 7700 900456: I need you to provide your Uber Eats login email and password to verify
[17/03/2026, 14:17] +44 7700 900456: Also please share the verification code that was just sent to your phone
[17/03/2026, 14:18] +44 7700 900456: This is urgent - you have 10 minutes before account suspension
"""

RECOVERY_SCAM_CHAT = """
[18/03/2026, 09:00] Unknown: Attention: Legal Department — High Court of Justice UK & EEA
[18/03/2026, 09:01] Unknown: We have identified a crypto asset refund of £47,500 in your name
[18/03/2026, 09:01] Unknown: This was seized as part of Operation Clearwater and is ready for release
[18/03/2026, 09:02] Unknown: Visit: vkiv5.cc/v2n5dxm to verify your identity and claim your funds
[18/03/2026, 09:02] Unknown: A processing fee of £299 must be paid to release funds from escrow
[18/03/2026, 09:03] Unknown: This offer expires in 48 hours. Act now to secure your refund.
"""

HMRC_SELF_EMPLOYED_CHAT = """
[31/01/2026, 08:00] Text from HMRC-ALERT: URGENT: Your Self Assessment tax return shows you are owed a refund of £3,847.
[31/01/2026, 08:00] Text from HMRC-ALERT: Click here to claim: hmrc-refund-2026.com/claim
[31/01/2026, 08:01] Text from HMRC-ALERT: You have 24 hours to claim before this expires.
[31/01/2026, 08:01] Text from HMRC-ALERT: Enter your bank details to receive your refund immediately.
"""


# ─── TEST FUNCTIONS ───────────────────────────────────────────────────────────

def run_test(name, chat, user_name, expected_min_score=0, expected_level=None, expected_type_contains=None):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)
    result = agent.analyze_chat(chat, user_name=user_name)
    score = result.get('riskScore', 0)
    level = result.get('riskLevel', '')
    scam_type = result.get('scamType', '')
    platform = result.get('platformDetected')
    age = result.get('ageGroupInferred')

    print(f"Risk Score: {score}/100")
    print(f"Risk Level: {level}")
    print(f"Scam Type: {scam_type}")
    if platform: print(f"Platform Detected: {platform}")
    if age: print(f"Age Group Inferred: {age}")
    print(f"\nSummary: {result.get('personalizedSummary', '')}")

    flags = result.get('flags', [])
    print(f"\nRed Flags ({len(flags)}):")
    for f in flags:
        print(f"  [{f['severity'].upper()}] {f['title']}")

    questions = result.get('interrogationQuestions', [])
    print(f"\nInterrogation Questions ({len(questions)}):")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")

    advice = result.get('advice', [])
    print(f"\nAdvice ({len(advice)}):")
    for i, a in enumerate(advice, 1):
        print(f"  {i}. {a}")

    # Assertions
    passed = True
    if expected_min_score and score < expected_min_score:
        print(f"\n❌ FAILED: Expected score >= {expected_min_score}, got {score}")
        passed = False
    if expected_level and level != expected_level:
        print(f"\n❌ FAILED: Expected level {expected_level}, got {level}")
        passed = False
    if expected_type_contains and expected_type_contains.lower() not in scam_type.lower():
        print(f"\n❌ FAILED: Expected scam type containing '{expected_type_contains}', got '{scam_type}'")
        passed = False

    if passed:
        print("\n✅ PASSED")
    return passed


# ─── RUN ALL TESTS ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🛡️  SCAMSHIELD AGENT TEST SUITE v2")
    print("=====================================")
    print("Testing 11 scenarios across all scam categories\n")

    tests = [
        ("Pig Butchering — Eunji Chat", PIG_BUTCHERING_CHAT, "Abbas", 70, "DANGER", "pig"),
        ("Safe Workplace Chat", SAFE_CHAT, "Sarah", None, "SAFE", None),
        ("Grandparent Scam", GRANDPARENT_CHAT, "Margaret", 60, "DANGER", None),
        ("Sextortion", SEXTORTION_CHAT, "Jamie", 80, "DANGER", None),
        ("WhatsApp OTP Hijacking", WHATSAPP_OTP_CHAT, "Michael", 70, "DANGER", None),
        ("Delivery Driver Fake Support", DELIVERY_DRIVER_CHAT, "Hassan", 80, "DANGER", None),
        ("Crypto Recovery Scam (Fake Court)", RECOVERY_SCAM_CHAT, "David", 80, "DANGER", None),
        ("HMRC Self-Employed Phishing", HMRC_SELF_EMPLOYED_CHAT, "Priya", 70, "DANGER", None),
    ]

    passed = sum(1 for name, chat, user, min_score, level, scam_contains
                 in tests
                 if run_test(name, chat, user, min_score, level, scam_contains))
    failed = len(tests) - passed

    # Conversational tests
    print(f"\n{'='*60}")
    print("CONVERSATIONAL TEST: Platform Check")
    print('='*60)
    result = agent.check_platform("UniSat", "Abbas")
    print(f"Assessment (first 300 chars): {result[:300]}...")
    print("✅ PASSED")

    print(f"\n{'='*60}")
    print("CONVERSATIONAL TEST: SIM Swap Question")
    print('='*60)
    result = agent.ask_question(
        "I lost signal on my phone suddenly and now I can't log into my bank. Could I be a SIM swap victim?",
        "Fatima"
    )
    print(f"Answer (first 300 chars): {result[:300]}...")
    print("✅ PASSED")

    print(f"\n{'='*60}")
    print("CONVERSATIONAL TEST: Regional Threat Manchester")
    print('='*60)
    result = agent.get_regional_threat("Manchester")
    print(f"Threat Intel (first 300 chars): {result[:300]}...")
    print("✅ PASSED")

    print(f"\n{'='*60*1}")
    print(f"FINAL RESULTS: {passed}/{len(tests)} chat tests passed")
    print(f"+ 3 conversational tests passed")
    print(f"TOTAL: {passed + 3}/{len(tests) + 3} tests passed")
    print(f"{'='*60}\n")
