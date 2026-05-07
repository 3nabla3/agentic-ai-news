# agentic-ai-news

A GitHub Actions pipeline that sends a weekly email digest covering the latest developments in agentic programming and AI cybersecurity.

## How it works

Every Tuesday at 6am EST, the workflow:
1. Queries the [Perplexity](https://www.perplexity.ai/) Sonar model to search the web and summarize the top 5 week-over-week changes in each of two topics
2. Sends the result as an HTML email via [Resend](https://resend.com/)

The digest covers the last 7 days and focuses on what has changed in the industry since the previous week.

## Setup

### 1. Fork or clone this repository

### 2. Add the following repository secrets

Go to **Settings > Secrets and variables > Actions** and add:

| Secret | Description |
|---|---|
| `PERPLEXITY_KEY` | Your Perplexity API key |
| `RESEND_KEY` | Your Resend API key |
| `TO_EMAIL` | The email address to send the digest to |

### 3. Enable GitHub Actions

The workflow runs automatically on the schedule. You can also trigger it manually from the **Actions** tab using the "Run workflow" button.

## Topics covered

- **Agentic programming** — frameworks, models, SDKs, open-source releases
- **AI cybersecurity** — threats, tools, research, incidents
