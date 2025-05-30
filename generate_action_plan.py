import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

def get_action_plan(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert credit repair assistant."},
            {"role": "user", "content": f"Analyze this credit report and identify collections, charge-offs, late payments, and generate a round 1 dispute plan:\n{text[:4000]}"}
        ]
    )
    return response.choices[0].message.content