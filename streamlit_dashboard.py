import streamlit as st
import os
import pandas as pd
from datetime import datetime
from extract_pdf import extract_text_from_pdf
from generate_action_plan import get_action_plan
from generate_letter import generate_dispute_letter
from save_letter_pdf import save_letter_as_pdf
from send_letter_lob import send_certified_letter
from dispute_tracker import log_dispute, get_last_dispute_info, needs_follow_up

st.title("Melissa's Credit Repair Assistant")

uploaded_file = st.file_uploader("Upload your credit report (.pdf)", type="pdf")
if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.success("✅ Credit report uploaded successfully.")

    bureau = st.selectbox("Which bureau are you disputing?", ["TransUnion", "Equifax", "Experian"])
    account_name = st.text_input("Enter the name of the account you're disputing")
    reason = st.text_area("Reason for dispute")

    if st.button("📬 Generate and Send Dispute Letter"):
        info = get_last_dispute_info(bureau, account_name)

        if info:
            if not needs_follow_up(bureau, account_name):
                st.warning(f"⚠️ This account was already disputed to {bureau} (Round {info['round']}) on {info['date_sent'].strftime('%Y-%m-%d')}.")
                st.stop()
            round_num = info["round"] + 1
        else:
            round_num = 1

        letter = generate_dispute_letter(account_name, reason)
        save_letter_as_pdf(letter)
        tracking_url = send_certified_letter(bureau, "dispute_letter.pdf")
        log_dispute(bureau, account_name, round_num)

        st.success(f"📨 Round {round_num} letter sent and logged!")
        st.markdown(f"[Track certified mail here]({tracking_url})")

# Show pending follow-ups (30+ days)
st.subheader("🕒 Pending Follow-Ups (30+ days)")
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
        st.info("✅ No follow-up disputes are currently due.")
