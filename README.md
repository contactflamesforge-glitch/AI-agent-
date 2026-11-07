# ColdMail Pro AI Agent

A service-agnostic AI assistant for researching an offer, segmenting an audience, and drafting personalized cold emails and follow-ups.

## Run locally
1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Run `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and add your OpenAI API key.
5. Run `streamlit run app.py`.

## Features
- Works for any legitimate service or B2B offer.
- Audience and segment-specific messaging.
- Prospect CSV import and opt-out suppression indicators.
- First emails, follow-ups, and break-up emails.
- Local quality checks plus optional AI review.
- Draft-only by default. Sending is disabled unless explicitly enabled, and each individual email requires a separate approval checkbox.

## CSV columns
Recommended: `email`, `first_name`, `company`, `role`, `industry`, `personalization`, `opted_out`.

## Safety
Use contacts only where you have a lawful basis. Respect opt-outs, identify yourself honestly, and follow applicable privacy and anti-spam laws. Do not send automatically or use fabricated personalization, proof, metrics, or claims. This software is not legal advice and cannot guarantee deliverability or results.

See [VIDEO_LEARNINGS.md](VIDEO_LEARNINGS.md) for the cold-email principles built into the agent. Run tests with `pytest`.
