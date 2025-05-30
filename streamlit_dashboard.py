import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from extract_pdf import extract_text_from_pdf
from generate_action_plan import get_dispute_items_with_retry
from generate_letter import generate_dispute_letter
from save_letter_pdf import save_letter_as_pdf
from send_letter_lob import send_certified_letter
from dispute_tracker import log_dispute, get_last_dispute_info, needs_follow_up

st.title("Melissa's Credit Repair Assistant")

# Step 1: Upload PDF and extract text
uploaded_file = st.file_uploader("Upload your credit report (.pdf)", type="pdf")
if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.success("✅ Credit report uploaded and read successfully.")

    # Step 2: Generate dispute items using GPT
    st.subheader("📄 AI-Generated Dispute Plan")

    with st.spinner("Analyzing report and generating dispute plan..."):
        try:
            items_json = get_dispute_items_with_retry(text)
        except Exception as e:
            st.error(f"❌ Failed to generate dispute plan: {e}")
            st.stop()

    # Attempt to sanitize and parse GPT output
    try:
        # Extract valid JSON if GPT adds extra text
        json_start = items_json.find('[')
        json_end = items_json.rfind(']') + 1
        clean_json = items_json[json_start:json_end]

        items = json.loads(clean_json)
    except Exception as e:
        st.error("⚠️ Error: Could not understand GPT output. Please check the credit report formatting.")
        st.text("Raw GPT output:")
        st.code(items_json, language="json")
        st.stop()

    # Step 3: Show each dispute item with a button to send it
    for item in items:
        bureau = item.get("bureau", "Unknown")
        account = item.get("account")
        reason = item.get("reason")

        if not bureau or not account or not reason:
            continue  # Skip incomplete entries

        st.markdown(f"---")
        st.markdown(f"### {account} ({bureau})")
        st.text(f"Reason: {reason}")

        if st.button(f"📬 Send dispute to {bureau} for {account}"):
            info = get_last_dispute_info(bureau, account)
            round_num = 1

            if info:
                if not needs_follow_up(bureau, account):
                    st.warning(f"⚠️ Already disputed (Round {info['round']}) on {info['date_sent'].strftime('%Y-%m-%d')}")
                    continue
                round_num = info["round"] + 1

            # Generate, save, and send the letter
            letter = generate_dispute_letter(account, reason)
            save_letter_as_pdf(letter)
            tracking_url = send_certified_letter(bureau, "dispute_letter.pdf")
            log_dispute(bureau, account, round_num)

            st.success(f"✅ Sent Round {round_num} dispute to {bureau} for {account}")
            st.markdown(f"[Track your certified mail here]({tracking_url})")

# Step 4: Show upcoming follow-ups
st.markdown("---")
st.subheader("🕒 Pending Follow-Ups (30+ days old)")
if os.path.exists("disputes.csv"):
    df = pd.read_csv("disputes.csv")
    followups = []
    seen = set()
    for _, row in df.iterrows():
        key = (row["bureau"], row["account"])
        if key in seen:
            continue
        seen.add(key)
        if needs_follow_up(row["bureau"], row["account"]):
            followups.append(row)
    if followups:
        st.dataframe(pd.DataFrame(followups))
    else:
        st.info("✅ No follow-up disputes are due yet.")

# Step 5: Show dispute history
st.markdown("---")
st.subheader("📜 Dispute History")

if os.path.exists("disputes.csv"):
    df = pd.read_csv("disputes.csv")
    df["date_sent"] = pd.to_datetime(df["date_sent"])
    df = df.sort_values(by="date_sent", ascending=False)

    st.dataframe(df[["bureau", "account", "round", "date_sent"]])
else:
    st.info("📭 No disputes have been logged yet.")

