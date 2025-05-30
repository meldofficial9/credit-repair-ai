import openai

client = openai.OpenAI(api_key=openai.api_key)

def generate_dispute_letter(account_name, reason):
    prompt = f"""
    Write a professional credit dispute letter for:
    Name: Melissa R Diaz Bravo
    Address: 2053 Great Falls Way, Orlando, FL 32824
    DOB: 01/09/1999
    SSN (last 4): 3173
    Phone: 407-821-7140
    Disputing Account: {account_name}
    Reason: {reason}
    Format as a letter for mailing to a credit bureau.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a credit dispute letter writer."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
