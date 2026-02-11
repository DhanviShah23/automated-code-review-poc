from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

def call_llm(prompt):
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON. No markdown, no text."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return res.choices[0].message.content