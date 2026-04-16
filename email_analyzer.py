import anthropic
import json


def analyze_email(client: anthropic.Anthropic, email_text: str) -> dict:
    """Analyze an email to extract intent, tone, key points, and required action."""
    prompt = f"""Analyze the following email and return a JSON object with these fields:
- sender_intent: what the sender wants or is communicating
- sender_tone: the emotional tone of the email (e.g. frustrated, friendly, urgent, formal)
- key_points: list of the main points raised
- required_action: what response or action is expected
- urgency: low | medium | high
- context_clues: any relevant context (e.g. ongoing relationship, complaint, request, inquiry)

Email:
{email_text}

Respond with ONLY valid JSON, no other text."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)
