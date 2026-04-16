import anthropic
from dataclasses import dataclass

TONES = {
    "professional": {
        "label": "Professional & Formal",
        "description": "Clear, polished, business-appropriate language. Structured and direct.",
    },
    "friendly": {
        "label": "Friendly & Warm",
        "description": "Conversational, personable, approachable. Builds rapport while still being helpful.",
    },
    "concise": {
        "label": "Concise & Direct",
        "description": "Brief, to-the-point, no fluff. Respects the reader's time.",
    },
}


@dataclass
class DraftResult:
    tone_key: str
    tone_label: str
    subject: str
    body: str


def generate_draft(
    client: anthropic.Anthropic,
    original_email: str,
    analysis: dict,
    tone_key: str,
    tone_info: dict,
) -> DraftResult:
    analysis_summary = "\n".join(
        f"- {k.replace('_', ' ').title()}: {v}" for k, v in analysis.items()
    )

    prompt = f"""You are drafting an email response. Write a reply that addresses the original email.

ORIGINAL EMAIL:
{original_email}

EMAIL ANALYSIS:
{analysis_summary}

TONE INSTRUCTION:
Write in a {tone_info['label']} tone. {tone_info['description']}

Instructions:
- Write a complete, ready-to-send email response
- Start with "Subject: " on the first line
- Leave a blank line, then write the email body
- Address all key points from the analysis
- Match the requested tone throughout
- Do not include any preamble or explanation — just the email itself"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()
    lines = text.split("\n", 2)

    subject = ""
    body = text
    if lines[0].lower().startswith("subject:"):
        subject = lines[0][len("subject:"):].strip()
        body = "\n".join(lines[1:]).strip()

    return DraftResult(
        tone_key=tone_key,
        tone_label=tone_info["label"],
        subject=subject,
        body=body,
    )


def generate_all_drafts(
    client: anthropic.Anthropic,
    original_email: str,
    analysis: dict,
) -> list[DraftResult]:
    drafts = []
    for tone_key, tone_info in TONES.items():
        draft = generate_draft(client, original_email, analysis, tone_key, tone_info)
        drafts.append(draft)
    return drafts
