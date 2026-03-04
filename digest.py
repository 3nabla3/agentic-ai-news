import requests, os, logging, time
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

REFUSAL_MARKERS = [
    "I cannot fulfill",
    "I cannot provide",
    "I'm unable to",
    "I am unable to",
    "do not contain information",
    "don't contain information",
    "cannot provide the response",
    "you would need:",
    "request a new search",
]

MAX_RETRIES = 3


def _looks_like_refusal(text):
    lower = text.lower()
    return any(marker.lower() in lower for marker in REFUSAL_MARKERS)


def _call_perplexity(time_range):
    today = datetime.today().strftime("%B %-d, %Y")
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {PERPLEXITY_KEY}"},
        json={
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a research assistant that produces an HTML email digest. "
                        "ALWAYS return valid HTML content with two sections and bullet points. "
                        "NEVER refuse or explain why you cannot answer. "
                        "If very recent results are sparse, include the most recent "
                        "relevant developments you can find."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Today is {today}. Search the web and summarize the most important "
                        f"recent developments from roughly {time_range} on:\n"
                        "1. Agentic programming (frameworks, models, SDKs, open-source releases)\n"
                        "2. AI cybersecurity (threats, tools, research, incidents)\n\n"
                        "Return ONLY raw HTML (no markdown, no code fences). "
                        "Use two <h2> sections with <ul> bullet points and "
                        "include <a href> source links. Max 5 items per section."
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

    return content.strip()


def fetch_digest():
    is_monday = datetime.today().weekday() == 0
    time_range = "the last 3 days (Saturday and Sunday)" if is_monday else "the last 24 hours"
    logger.info("Fetching digest for time range: %s", time_range)

    for attempt in range(1, MAX_RETRIES + 1):
        content = _call_perplexity(time_range)

        if not _looks_like_refusal(content):
            logger.info("Digest fetched successfully (%d characters)", len(content))
            return content

        logger.warning(
            "Attempt %d/%d returned a refusal response, retrying...",
            attempt, MAX_RETRIES
        )
        if attempt < MAX_RETRIES:
            time.sleep(2 ** attempt)

    # All retries returned refusals — broaden the time range and try once more
    logger.warning("All %d attempts refused. Retrying with broader time range.", MAX_RETRIES)
    content = _call_perplexity("the last week")

    if _looks_like_refusal(content):
        raise RuntimeError(
            "Perplexity repeatedly returned a refusal response. "
            "Email not sent to avoid delivering a broken digest."
        )

    logger.info("Digest fetched with broader time range (%d characters)", len(content))
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
