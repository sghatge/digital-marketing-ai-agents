<div align="center">

<img src="https://raw.githubusercontent.com/sghatge/sghatge/main/assets/portfolio/project-banner.svg" width="100%" alt="Sangram Ghatge engineering portfolio banner">

**INDEPENDENT ENGINEERING PORTFOLIO · DIGITAL MARKETING AI AGENTS**

[GitHub Profile](https://github.com/sghatge) · [Portfolio](https://sghatge.github.io/adobe-campaign-v8-governance/)

</div>

---

# Digital Marketing AI Lab

A lightweight marketing-workflow prototype: one brief becomes a strategy, content drafts, campaign quality checks, and transparent performance calculations.

## Four agents
- **Campaign Strategist:** creates a practical plan from the goal, audience, channel, budget, and brand voice.
- **Content Studio:** generates editable social copy and email subject lines.
- **Campaign QA:** checks URL format, UTM field completeness, content presence, and common absolute-claim phrases.
- **Performance Analyst:** calculates delivery rate, approximate CTR, conversion rate, and cost per conversion, with basic data-quality notes.

The app works without API credentials. Optional AI-assisted copy is available when a Gemini key is configured server-side.

## Run locally (Python 3.10+)

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional Gemini mode
1. Create a key in [Google AI Studio](https://aistudio.google.com/).
2. Set `GEMINI_API_KEY` in your environment or hosting secrets.
3. Optionally set `GEMINI_MODEL` to a model available to your account; default is `gemini-2.5-flash`.
4. Restart the app and click **Enhance strategy and content with AI**.

PowerShell for the current terminal:
```powershell
$env:GEMINI_API_KEY="your-key"
streamlit run app.py
```

Never commit API keys. Provider quotas, pricing, model access, and data terms can change.

## Deploy to Streamlit Community Cloud
1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and connect GitHub.
2. Select the repository and branch.
3. Set the branch to `main` and the app file path to `app.py`.
4. Deploy. Add `GEMINI_API_KEY` in app secrets only if AI mode is wanted.
5. Verify the public URL in a private/incognito browser.

Hosting limits and availability are controlled by the provider.

## Tests
From this folder:
```bash
python -m unittest discover -s tests -v
```

## 60–90 second LinkedIn demo
1. Enter a fictional goal and audience.
2. Show the campaign blueprint and test plan.
3. Edit the social post and subject lines.
4. Run QA with a missing UTM value, then correct it.
5. Enter sample metrics and explain the calculations.
6. Share the repository and live demo links.

## Limitations and safe use
- No connection to live ad, email, CRM, or analytics accounts.
- URL checks validate format only; they do not open or verify links.
- Copy checks are lightweight and are not legal, brand, or privacy approval.
- Metrics are arithmetic only; confirm event definitions, attribution, deduplication, and reporting windows.
- Human review is required before publishing or spending money.
- Use fictional or sanitized data for public demonstrations.


## CampaignPulse AI — Adobe Campaign Edition

The CampaignPulse AI V1 experience is available as a new page in the Streamlit multipage app. It accepts aggregate campaign statistics or CSV uploads, calculates KPIs deterministically, flags data-quality issues, and recommends Adobe Campaign operational checks without connecting to an Adobe Campaign instance.

- [CampaignPulse V1 specification](README_CAMPAIGNPULSE.md)
- [Creator playbook for ModletHub](modlethub/CAMPAIGNPULSE_AI_PLAYBOOK.md)
- [Structured creator manifest](modlethub/campaignpulse_manifest.json)
- [Oliver-ready creator submission](modlethub/CREATOR_SUBMISSION.md)
- [Input contract v1.1](schemas/campaign_input_v1.1.json)
- [Output contract v1.0](schemas/campaign_output_v1.0.json)

Public demos use fictional aggregate data. No recipient-level data, credentials, broadlogs, or production delivery logs are accepted.
