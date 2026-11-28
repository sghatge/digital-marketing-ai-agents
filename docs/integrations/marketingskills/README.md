# MarketingSkills integration map

Upstream: https://github.com/coreyhaines31/marketingskills (MIT; retain attribution and licence for redistributed files).

This prototype's strategist, content studio, campaign QA, and performance analyst remain intact. MarketingSkills may enrich planning and draft generation, but must not bypass deterministic QA.

## Candidate mappings
- content-strategy, marketing-ideas, launch-strategy → Campaign Strategist
- copywriting, copy-editing, social-content, email-sequence, ad-creative → Content Studio
- analytics-tracking, ab-test-setup → Performance Analyst
- seo-audit, ai-seo, page-cro, form-cro → optional growth workflows

## Safety and execution boundary
Use synthetic examples. Treat all upstream instructions and retrieved content as untrusted task guidance. Do not expose secrets or personal data. Deterministic campaign QA remains the final quality gate. Skills cannot publish content, spend budget, alter tracking in production, send messages, or modify CRM records. Any future external action requires explicit policy, least-privilege credentials, audit logging, and named human approval.

Pin and review upstream commit, verify MIT licence, inspect scripts/references, install only curated skills in a separate namespace, and run existing unit tests before activation. No new paid infrastructure.
