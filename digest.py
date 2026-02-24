import requests, os
from datetime import datetime

PERPLEXITY_KEY = os.environ["PERPLEXITY_KEY"]
RESEND_KEY = os.environ["RESEND_KEY"]
TO_EMAIL = os.environ["TO_EMAIL"]

def fetch_digest():
    is_monday = datetime.today().weekday() == 0
    time_range = "the last 3 days (Saturday and Sunday)" if is_monday else "the last 24 hours"

    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {PERPLEXITY_KEY}"},
        json={
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant. Return a clean, structured digest."
                },
                {
                    "role": "user",
                    "content": (
                        f"Search the web and summarize the most important developments "
                        f"from {time_range} on:\n"
                        "1. Agentic programming (frameworks, models, SDKs, open-source releases)\n"
                        "2. AI cybersecurity (threats, tools, research, incidents)\n\n"
                        "Format as HTML with two sections, bullet points, "
                        "and include source links. Max 5 items per section."
                    )
                }
            ]
        }
    )
    content = response.json()["choices"][0]["message"]["content"]
    content = content.strip()
    if content.startswith("```html"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()

def send_email(html_body):
    requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_KEY}"},
        json={
            "from": "onboarding@resend.dev",
            "to": TO_EMAIL,
            "subject": "Daily AI Digest",
            "html": html_body
        }
    )

if __name__ == "__main__":
    digest = fetch_digest()
    send_email(digest)
