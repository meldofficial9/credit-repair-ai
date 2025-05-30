import streamlit as st
from extract_pdf import extract_text_from_pdf
from generate_action_plan import get_action_plan
from generate_letter import generate_dispute_letter
from save_letter_pdf import save_letter_as_pdf
from send_letter_lob import send_certified_letter
from dispute_tracker import log_dispute, has_dispute_been_sent

st.title("Melissa's Credit Repair Assistant")

uploaded_file = st.file_uploader("Upload your credit report (.pdf)", type="pdf")
if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.success("Credit report uploaded successfully.")

    bureau = st.selectbox("Which bureau are you disputing?", ["TransUnion", "Equifax", "Experian"])
    account_name = st.text_input("Enter the name of the account you're disputing")
    reason = st.text_area("Reason for dispute")

    if st.button("Generate and Send Dispute Letter"):
        if has_dispute_been_sent(bureau, account_name):
            st.warning("This account has already been disputed to this bureau.")
        else:
            letter = generate_dispute_letter(account_name, reason)
            save_letter_as_pdf(letter)
            tracking_url = send_certified_letter(bureau, "dispute_letter.pdf")
            log_dispute(bureau, account_name, round_num=1)
            st.success("📬 Letter sent and logged!")
            st.markdown(f"[Track the letter here]({tracking_url})")