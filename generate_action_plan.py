import os
import openai
import time
from openai import RateLimitError

# ✅ Define the OpenAI client (new SDK pattern)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_dispute_items(text):
    prompt = f"""
    Read the following credit report and extract ALL negative items (collections, charge-offs, late payments, etc.).
    For each one, return:
    - Bureau (TransUnion, Experian, or Equifax if possible — or just say 'Unknown')
    - Account name
    - Suggested dispute reason (keep it simple)

    Format the output as JSON like this:
    [
      {{"bureau": "Experian", "account": "Capital One", "reason": "This account is not mine"}},
      ...
    ]

    Credit Report:
    {text[:4000]}
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a credit dispute specialist."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def get_dispute_items_with_retry(text, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return get_dispute_items(text)
        except RateLimitError:
            if attempt < retries - 1:
                wait_time = delay * (2 ** attempt)  # exponential backoff
                print(f"Rate limit hit, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Raising RateLimitError.")
                raise


