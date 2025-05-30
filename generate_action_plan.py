import openai

client = openai.OpenAI(api_key=openai.api_key)

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
