import streamlit as st
import lob

lob.api_key = st.secrets["LOB_API_KEY"]

bureau_addresses = {
    "TransUnion": {
        "name": "TransUnion",
        "address_line1": "P.O. Box 2000",
        "address_city": "Chester",
        "address_state": "PA",
        "address_zip": "19016"
    },
    "Experian": {
        "name": "Experian",
        "address_line1": "475 Anton Blvd",
        "address_city": "Costa Mesa",
        "address_state": "CA",
        "address_zip": "92626"
    },
    "Equifax": {
        "name": "Equifax",
        "address_line1": "P.O. Box 740256",
        "address_city": "Atlanta",
        "address_state": "GA",
        "address_zip": "30374"
    }
}

def send_certified_letter(bureau_name, pdf_path):
    to_address = bureau_addresses.get(bureau_name)
    if not to_address:
        raise ValueError("Invalid bureau name provided.")

    letter = lob.letters.create(
        description=f"Dispute Letter to {bureau_name}",
        to_address=to_address,
        from_address={
            "name": "Melissa R Diaz Bravo",
            "address_line1": "2053 Great Falls Way",
            "address_city": "Orlando",
            "address_state": "FL",
            "address_zip": "32824"
        },
        file=open(pdf_path, 'rb'),
        color=False,
        mail_type="certified"
    )

    return letter["tracking_events_url"]
