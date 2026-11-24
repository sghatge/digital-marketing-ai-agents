# ModletHub Creator Submission — CampaignPulse AI

## Listing title
CampaignPulse AI — Adobe Campaign Edition

## One-line promise
Paste the numbers. Understand what happened. Know what to check next.

## Short description
CampaignPulse AI helps Adobe Campaign practitioners turn aggregate email campaign statistics into a clear campaign health assessment, likely issue areas, and prioritized operational checks. It combines deterministic KPI calculations with practical Adobe Campaign v8 operational guidance. No Adobe Campaign integration, credentials, or production data are required.

## Who it is for
- Adobe Campaign Classic v7/v8 practitioners
- CRM and marketing operations managers
- Email campaign analysts and deliverability specialists
- Marketing technology consultants who need a quick, evidence-led campaign review

## The job it helps with
After an email send, practitioners often have a set of delivery and engagement numbers but need to interpret them quickly and decide what to investigate. CampaignPulse turns the supplied aggregate counts into a consistent diagnostic workflow.

## Inputs
Required:
- Sent
- Delivered
- Hard bounces
- Soft bounces
- Unique opens
- Unique clicks
- Unsubscribes

Optional:
- Campaign name and type
- Metric source (ACC v7, ACC v8, another ESP, manual, synthetic)
- Send date and reporting date
- Audience type and industry
- Other/ignored errors
- User-defined thresholds in the configuration

## Method
1. Capture aggregate metrics through manual entry or CSV.
2. Validate required values and impossible relationships.
3. Reconcile delivered and recorded failure counts with a configurable tolerance.
4. Calculate delivery, bounce, open, click, CTOR and unsubscribe rates deterministically.
5. Apply transparent configurable rules.
6. Present findings with evidence status, confidence and possible explanations.
7. Map findings to Adobe Campaign operational checks.
8. Let the practitioner approve follow-up actions and export the report.

## Outputs
- Health classification: Healthy, Watch, At risk or Critical
- KPI summary
- Data-quality warnings and review notes
- Evidence-labelled findings
- Prioritized operational checks
- Practitioner checklist or management summary
- Downloadable Markdown and JSON reports

## Three demo scenarios
1. Healthy campaign — stable delivery and engagement, with an unsubscribe signal to monitor.
2. Poor deliverability — elevated hard/soft bounce rates and a critical health result.
3. Declining engagement — strong delivery but weak open and click rates.

All examples are fictional and aggregate-only.

## AI-agent instructions
An agent using this playbook should:
- Follow the canonical input contract in `schemas/campaign_input_v1.1.json`.
- Use the deterministic KPI definitions and validation rules.
- Preserve the difference between observed evidence, possible explanations and recommended checks.
- Never claim to have inspected an Adobe Campaign instance.
- Never invent root causes, benchmarks or platform state.
- Keep creator attribution with the method when summarizing or reusing it.
- Ask a human practitioner to verify findings and approve any operational change.

## Important boundaries
CampaignPulse is a standalone decision-support tool. It does not authenticate to, inspect, or modify Adobe Campaign. It cannot verify actual delivery logs, quarantine records, retry queues, workflow state, IP reputation or domain-level failure reasons without evidence supplied by the practitioner.

Do not upload recipient-level PII, email addresses, broadlogs, production delivery logs, credentials or confidential client information. Use synthetic or sanitized aggregate data only.

Open rates are directional and may be inflated by privacy features. Thresholds are editable starter rules, not universal industry benchmarks or an Adobe-certified score.

## Creator attribution
**Sangram Ghatge** — CRM and Marketing Technology professional focused on Adobe Campaign, campaign operations, deliverability, automation and applied AI for marketing operations.

## Supporting assets
- Interactive application: existing Digital Marketing AI Lab Streamlit deployment, CampaignPulse AI page
- Source: https://github.com/sghatge/digital-marketing-ai-agents
- V1 specification: https://github.com/sghatge/digital-marketing-ai-agents/blob/main/README_CAMPAIGNPULSE.md
- Detailed playbook: https://github.com/sghatge/digital-marketing-ai-agents/blob/main/modlethub/CAMPAIGNPULSE_AI_PLAYBOOK.md
- Manifest: https://github.com/sghatge/digital-marketing-ai-agents/blob/main/modlethub/campaignpulse_manifest.json

## Publication note
This is a prepared creator submission package, not a submission to ModletHub. Confirm the creator licence, attribution, deletion, AI reuse, exclusivity and commercial terms before publishing the workflow.
