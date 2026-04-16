#!/usr/bin/env python3
"""Email Response Drafting Tool

Usage:
    python main.py                        # Interactive mode (paste email)
    python main.py --file email.txt       # Read email from file
    python main.py --email "email text"   # Pass email as argument
    python main.py --output drafts.txt    # Save drafts to file
"""

import argparse
import sys
import os
import anthropic

from email_analyzer import analyze_email
from draft_generator import generate_all_drafts

DIVIDER = "=" * 70
SECTION = "-" * 70


def read_email_from_stdin() -> str:
    print("Paste your email below. When done, press Ctrl+D (Unix) or Ctrl+Z (Windows):")
    print(SECTION)
    lines = []
    try:
        for line in sys.stdin:
            lines.append(line)
    except EOFError:
        pass
    return "".join(lines).strip()


def format_analysis(analysis: dict) -> str:
    lines = ["\nEMAIL ANALYSIS", SECTION]
    for key, value in analysis.items():
        label = key.replace("_", " ").title()
        if isinstance(value, list):
            lines.append(f"{label}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{label}: {value}")
    return "\n".join(lines)


def format_drafts(drafts) -> str:
    lines = ["\nGENERATED RESPONSE DRAFTS", DIVIDER]
    for i, draft in enumerate(drafts, 1):
        lines.append(f"\nDRAFT {i}: {draft.tone_label.upper()}")
        lines.append(SECTION)
        if draft.subject:
            lines.append(f"Subject: {draft.subject}")
            lines.append("")
        lines.append(draft.body)
        lines.append(DIVIDER)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate 3 email response drafts in different tones."
    )
    parser.add_argument("--file", "-f", help="Path to a file containing the email")
    parser.add_argument("--email", "-e", help="Email text passed directly as argument")
    parser.add_argument("--output", "-o", help="Save output to this file")
    args = parser.parse_args()

    if args.email:
        email_text = args.email
    elif args.file:
        with open(args.file, "r") as fh:
            email_text = fh.read().strip()
    else:
        email_text = read_email_from_stdin()

    if not email_text:
        print("Error: no email provided.", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print("\nAnalyzing email...", flush=True)
    analysis = analyze_email(client, email_text)
    analysis_output = format_analysis(analysis)
    print(analysis_output)

    print("\nGenerating 3 response drafts...", flush=True)
    drafts = generate_all_drafts(client, email_text, analysis)
    drafts_output = format_drafts(drafts)
    print(drafts_output)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(analysis_output + "\n")
            fh.write(drafts_output + "\n")
        print(f"\nOutput saved to: {args.output}")


if __name__ == "__main__":
    main()
