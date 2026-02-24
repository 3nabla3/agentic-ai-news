import requests, os, logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

PERPLEXITY_KEY = os.environ["PERPLEXITY_KEY"]
RESEND_KEY = os.environ["RESEND_KEY"]
TO_EMAIL = os.environ["TO_EMAIL"]

def fetch_digest():
    is_monday = datetime.today().weekday() == 0
    time_range = "the last 3 days (Saturday and Sunday)" if is_monday else "the last 24 hours"
    logger.info("Fetching digest for time range: %s", time_range)

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
    logger.info("Perplexity responded with status %s", response.status_code)
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    content = content.strip()

    if content.startswith("```html"):
        logger.debug("Stripping ```html code fence")
        content = content[7:]
    elif content.startswith("```"):
        logger.debug("Stripping ``` code fence")
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()
    logger.info("Digest fetched successfully (%d characters)", len(content))
    return content

def send_email(html_body):
    logger.info("Sending email to %s", TO_EMAIL)
    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_KEY}"},
        json={
            "from": "onboarding@resend.dev",
            "to": TO_EMAIL,
            "subject": "Daily AI Digest",
            "html": html_body
        }
    )
    logger.info("Resend responded with status %s", response.status_code)
    response.raise_for_status()
    logger.info("Email sent successfully")

if __name__ == "__main__":
    logger.info("Starting daily AI digest pipeline")
    digest = fetch_digest()
    send_email(digest)
    logger.info("Pipeline completed successfully")
