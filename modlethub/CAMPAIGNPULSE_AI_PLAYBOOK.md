# CampaignPulse AI — Adobe Campaign Edition

**Creator:** Sangram Ghatge  
**Category:** Marketing Operations · Email Campaign Analytics · AI-assisted workflow  
**Version:** 1.0 · **Status:** V1 prototype  
**Execution mode:** Human-guided, standalone, no Adobe Campaign connection

## Outcome

Turn aggregate email campaign statistics into a reproducible health assessment, evidence-backed issue list, and prioritized operational checks.

## When to use

Use this playbook after an email campaign has produced a reporting snapshot. It is designed for Adobe Campaign practitioners and can also accept aggregate metrics from other email service providers.

## Required inputs

- Sent
- Delivered
- Hard bounces
- Soft bounces
- Unique opens
- Unique clicks
- Unsubscribes

Optional context: campaign name, send/reporting dates, source system, campaign type, audience type, industry, other error categories, and user-defined thresholds.

## Workflow

1. **Capture** aggregate metrics through the manual form or CSV upload.
2. **Normalize** values into the CampaignPulse canonical input contract.
3. **Validate** required counts, impossible relationships, reporting maturity, and reconciliation.
4. **Calculate** delivery, bounce, open, click, CTOR, and unsubscribe rates deterministically.
5. **Diagnose** against configurable thresholds. Thresholds are starter defaults, not universal industry benchmarks.
6. **Explain** each finding with observed evidence, possible explanations, confidence, and checks.
7. **Review** the recommended actions as a practitioner. CampaignPulse does not execute changes.
8. **Export** the report for operational follow-up or management communication.

## Metric definitions

- Delivery rate = delivered / sent × 100
- Hard-bounce rate = hard bounces / sent × 100
- Soft-bounce rate = soft bounces / sent × 100
- Total bounce rate = (hard + soft + ignored + other errors) / sent × 100
- Open rate = unique opens / delivered × 100
- Click-through rate = unique clicks / delivered × 100
- Click-to-open rate = unique clicks / unique opens × 100
- Unsubscribe rate = unsubscribes / delivered × 100

A zero denominator returns no rate, never zero. Open tracking is directional and may be inflated by privacy features such as Apple Mail Privacy Protection.

## Evidence and safety boundaries

- **Observed:** arithmetic and relationships directly present in supplied aggregate data.
- **Inferred:** possible causes that require human investigation.
- **Recommended check:** a location or report a practitioner may inspect inside Adobe Campaign.
- **Not verified:** live delivery logs, actual quarantine records, workflow state, retry queues, IP reputation, or domain-level failure reasons.

CampaignPulse does not connect to, inspect, authenticate to, or modify Adobe Campaign. It does not accept recipient-level PII, broadlogs, production delivery logs, or credentials. Use synthetic or sanitized aggregate data only.

## Human approval

A practitioner must verify the evidence in the source platform and approve any operational change. CampaignPulse provides decision support, not a deployment or deliverability guarantee.

## Reproducibility

KPI calculations and rule-based findings are deterministic for the same input and threshold configuration. Optional LLM explanations must not change metrics, severity, evidence, or the action set. If no model is configured, the rules-based report remains fully usable.

## Suggested evaluation scenarios

1. Healthy delivery and engagement.
2. Poor deliverability with elevated hard/soft bounces.
3. Strong delivery but declining engagement.

## Creator attribution

Created by **Sangram Ghatge**. This playbook is intended as a reusable method for human practitioners and AI agents. Publication, licensing, AI reuse and commercial terms remain subject to the creator terms agreed with ModletHub.
