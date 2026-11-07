import os
import json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from coldmail.agent import ColdMailAgent
from coldmail.mailer import send_approved_email
from coldmail.quality import local_quality_check

load_dotenv()
st.set_page_config(page_title="ColdMail Pro", page_icon="✉️", layout="wide")
st.title("✉️ ColdMail Pro — AI Cold Email Agent")
st.caption("Specific, evidence-led cold emails for any legitimate service. Draft-only by default.")

with st.sidebar:
    st.header("Configuration")
    provider = st.selectbox("AI provider", ["Google Gemini (free tier)"], index=0)
    api_key = st.text_input(
        "Google Gemini API key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Create a key in Google AI Studio. Keep it private; never commit it to GitHub."
    )
    model = st.text_input("Model", value=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"))
    st.info("Gemini offers a free API tier with usage limits. Free-tier data may be used by Google to improve its products. Avoid entering confidential or sensitive prospect information.")
    st.caption("Your API key is used only for generation. Never share it or commit it to GitHub.")

create_tab, leads_tab, notes_tab = st.tabs(["Create emails", "Lead CSV", "Campaign notes"])
with create_tab:
    st.subheader("Build the offer and audience picture")
    left, right = st.columns(2)
    with left:
        offer = st.text_area(
            "What service are you offering?", height=120,
            placeholder="What do you do, who is it for, and what changes after they use it?"
        )
        proof = st.text_area(
            "Verified proof (optional)", height=90,
            placeholder="Real results, relevant experience, examples, credentials, or a concrete process. No guesses."
        )
        differentiator = st.text_area(
            "What makes your way of doing it credible or different? (optional)",
            height=80, placeholder="A real method, useful detail, or reason to believe. Leave blank if none."
        )
    with right:
        audience = st.text_area(
            "Who do you want to reach?", height=120,
            placeholder="Industry, role, company type/size, location, and buying situation."
        )
        segment = st.text_input(
            "Audience segment (optional)",
            placeholder="A distinct group with a shared situation or need"
        )
        segment_problem = st.text_area(
            "What problem or opportunity matters to this segment? (optional)",
            height=80, placeholder="Separate what you know from what you suspect."
        )
        desired_outcome = st.text_area(
            "What outcome do they want? (optional)",
            height=80, placeholder="Describe a practical result without promising it."
        )
    prospect_raw = st.text_area(
        "Prospect-specific facts + source (optional)",
        placeholder="Example: Their menu page lists no prices (checked on their official website on [date]). Only include facts you actually verified."
    )
    st.caption("No prospect research? That's fine. The agent must not pretend it researched someone. It will write to the audience segment without inventing personal observations.")
    step = st.selectbox("Email type", ["First email", "Follow-up 1", "Follow-up 2", "Break-up email"])
    if st.button("Generate cold email", type="primary", disabled=not (api_key and offer.strip() and audience.strip())):
        try:
            prospect = json.loads(prospect_raw) if prospect_raw.strip().startswith("{") else {"verified_context": prospect_raw} if prospect_raw.strip() else {}
            with st.spinner("Writing and checking for relevance, truth and generic wording..."):
                draft = ColdMailAgent(api_key, model, provider="gemini").generate(
                    offer, audience, proof, prospect, segment, step,
                    segment_problem, desired_outcome, differentiator
                )
            st.session_state["draft"] = draft
            st.session_state["offer"] = offer
            st.session_state["audience"] = audience
            st.session_state["verified_prospect"] = prospect
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
    draft = st.session_state.get("draft")
    if draft:
        st.divider()
        st.subheader("Draft")
        st.text_input("Subject", value=draft.get("subject", ""), key="subject_edit")
        st.text_area("Email body", value=draft.get("email", ""), height=220, key="body_edit")
        st.write("Why this angle:", draft.get("rationale", ""))
        st.write("Personalization actually used:", draft.get("personalization_used", ""))
        st.write("Evidence used:", draft.get("evidence_used", "None stated"))
        if draft.get("assumptions_or_missing_facts"):
            st.warning("Facts to verify / information missing: " + str(draft["assumptions_or_missing_facts"]))
        if draft.get("segment_fit"):
            st.write("Segment fit:", draft["segment_fit"])
        score = draft.get("quality_score")
        if score is not None:
            st.metric("Agent's honest draft score", f"{score}/10")
        if draft.get("quality_notes"):
            st.caption("Score explanation: " + str(draft["quality_notes"]))
        check = local_quality_check(
            st.session_state.get("subject_edit", draft.get("subject", "")),
            st.session_state.get("body_edit", draft.get("email", "")),
            verified_facts=st.session_state.get("verified_prospect", {})
        )
        if check["passed"]:
            st.success(f"Local checks passed ({check['word_count']} words). This is not a guarantee; review the facts before use.")
        else:
            st.warning("Fix these before use: " + " | ".join(check["issues"]))
        if st.button("AI quality review", disabled=not api_key):
            try:
                review = ColdMailAgent(api_key, model, provider="gemini").review(
                    st.session_state["body_edit"],
                    st.session_state.get("offer", ""),
                    st.session_state.get("audience", "")
                )
                st.json(review)
            except Exception as exc:
                st.error(str(exc))
        st.divider()
        st.subheader("Optional one-at-a-time sending")
        st.caption("Requires ENABLE_EMAIL_SENDING=true plus explicit approval of this exact message.")
        recipient = st.text_input("Recipient email")
        lawful = st.checkbox("I confirm I have a lawful basis to contact this person and they have not opted out.")
        approved = st.checkbox("I reviewed and explicitly approve sending this exact email.")
        if st.button("Send this approved email", disabled=not (recipient and lawful and approved)):
            try:
                send_approved_email(recipient, st.session_state["subject_edit"], st.session_state["body_edit"])
                st.success("Email sent.")
            except Exception as exc:
                st.error(f"Not sent: {exc}")

with leads_tab:
    st.write("Upload a CSV for review. Uploading does not send emails.")
    uploaded = st.file_uploader("Prospect CSV", type=["csv"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            st.dataframe(df, use_container_width=True)
            if "opted_out" in df.columns:
                mask = df["opted_out"].astype(str).str.lower().isin(["true", "1", "yes", "y"])
                st.warning(f"{int(mask.sum())} opted-out contact(s) should be suppressed.")
            st.download_button("Download CSV", df.to_csv(index=False), "prospects_reviewed.csv", "text/csv")
        except Exception as exc:
            st.error(f"CSV error: {exc}")

with notes_tab:
    st.text_area("Campaign learnings, replies, objections, and next tests", height=220)
    st.caption("Learn from positive replies, qualified conversations, and objections—not opens alone.")
