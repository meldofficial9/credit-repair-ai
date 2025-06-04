import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
import streamlit_authenticator as stauth

from extract_pdf import extract_text_from_pdf
from generate_action_plan import get_dispute_items_with_retry
from generate_letter import generate_dispute_letter
from save_letter_pdf import save_letter_as_pdf
from send_letter_lob import send_certified_letter
from dispute_tracker import log_dispute, get_last_dispute_info, needs_follow_up

# ------------------------- AUTH -------------------------
names = ["Melissa Diaz"]
usernames = ["melissa"]
passwords = ["1234"]

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    {"usernames": {
        usernames[0]: {
            "name": names[0],
            "password": hashed_passwords[0]
        }
    }},
    "credit_app", "auth_token", cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("Incorrect username or password")
elif authentication_status is None:
    st.warning("Please enter your credentials")
elif authentication_status:
    authenticator.logout("Logout", "sidebar")

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

        try:
            items = json.loads(items_json)
        except json.JSONDecodeError:
            st.error("⚠️ Error: Could not understand GPT output. Please check the credit report formatting.")
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
                info = get_last_dispute_info(bureau, account, username)
                round_num = 1

                if info:
                    if not needs_follow_up(bureau, account, username):
                        st.warning(f"⚠️ Already disputed (Round {info['round']}) on {info['date_sent'].strftime('%Y-%m-%d')}")
                        continue
                    round_num = info["round"] + 1

                letter = generate_dispute_letter(account, reason)
                save_letter_as_pdf(letter)
                tracking_url = send_certified_letter(bureau, "dispute_letter.pdf")
                log_dispute(bureau, account, round_num, username)

                st.success(f"✅ Sent Round {round_num} dispute to {bureau} for {account}")
                st.markdown(f"[Track your certified mail here]({tracking_url})")

    # Step 4: Show upcoming follow-ups
    st.markdown("---")
    st.subheader("🕒 Pending Follow-Ups (30+ days old)")
    tracker_file = f"disputes_{username}.csv"
    if os.path.exists(tracker_file):
        df = pd.read_csv(tracker_file)
        followups = []
        seen = set()
        for _, row in df.iterrows():
            key = (row["bureau"], row["account"])
            if key in seen:
                continue
            seen.add(key)
            if needs_follow_up(row["bureau"], row["account"], username):
                followups.append(row)
        if followups:
            st.dataframe(pd.DataFrame(followups))
        else:
            st.info("✅ No follow-up disputes are due yet.")

