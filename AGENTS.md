# Campaign Link Doctor: agent and engineer instructions

This file applies to this repository unless a deeper `AGENTS.md` imposes stricter scope. It is an onboarding aid for new/existing agents and human software engineers, **not** an authorisation to publish, spend or deploy.

## Identity and status

Public, local-first campaign URL and UTM preflight with CLI and browser alpha; no telemetry, accounts, cookies, uploads or paid services.

## Operating contract

1. Read this file, project README, actual source, any nested instructions and test/runbook before editing.
2. Keep PRs focused; never self-merge, add telemetry/secrets, run paid services or claim tests/deployments you did not observe.
3. Respect original/licensed assets and all contributors' rights. Work from synthetic examples and never leak customer/private data.
4. Include in every handoff: branch/commit/PR, changed paths, exact test commands and results (or `NOT_RUN`), unverified assumptions and safe next action.

## Project-specific safeguards

1. Read `README.md` and `web/README.md` for CLI and browser boundaries. Never send user-supplied campaign URLs to online services.
2. Avoid printing personally identifying query-string values in tests or logs; use fabricated example URLs.
3. Browser accessibility and cross-device QA remain unverified per README; do not call the browser alpha production validated.
4. Test existing CLI and browser suites only with observed commands/results. Preserve deterministic offline behaviour.
