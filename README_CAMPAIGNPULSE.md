# CampaignPulse AI — Adobe Campaign Edition

A standalone campaign intelligence assistant built for Adobe Campaign practitioners. It turns aggregate email campaign metrics into deterministic KPIs, transparent diagnostic findings, and prioritized operational checks.

## Run locally

Python 3.10+

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open **CampaignPulse AI** from the Streamlit multipage navigation.

## Features

- Manual metric entry and CSV upload (multi-row CSV with row selection)
- Deterministic KPI calculations and validation
- Configurable starter thresholds in `config/campaignpulse_thresholds.json`
- Healthy, poor-deliverability and declining-engagement demo scenarios
- Evidence-labelled findings and Adobe Campaign operational checks
- Practitioner and Management report views
- Markdown and JSON downloads
- No Adobe Campaign connection or credentials required

## Deployment

The page is part of the existing Digital Marketing AI Lab Streamlit app. After the branch is merged to `main`, Streamlit Community Cloud should detect the repository update. If the existing deployment does not expose the new page automatically, check its app entry point remains `app.py` and restart/redeploy.

For a separate deployment, select this same repository, branch `main`, and app file `app.py` in [Streamlit Community Cloud](https://share.streamlit.io/).

## Test

```bash
python -m unittest discover -s tests -v
```

## Data safety

Use aggregate, synthetic or sanitized metrics only. Do not upload recipient-level data, email addresses, broadlogs, production delivery logs, confidential client information or credentials. The application does not inspect live Adobe Campaign records.

## ModletHub creator playbook

See [modlethub/CAMPAIGNPULSE_AI_PLAYBOOK.md](modlethub/CAMPAIGNPULSE_AI_PLAYBOOK.md) for the reusable workflow, evidence model, safety boundaries and creator attribution.
