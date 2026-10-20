# 30 Furies: independent release questions

A concrete 30-angle adversarial review, **not 30 separately activated agents or independent humans**. Re-run on every substantive change. Human-release approval and hosted CI remain separate from local machine checks.

| # | Fury question | Current evidence / caveat |
| -- | -- | -- |
| 01 | Is the user problem urgent? | Campaign tracking mistakes and PII |
| 02 | Can a novice try it now? | No-install module CLI |
| 03 | Can marketers use it without API accounts? | No accounts |
| 04 | Does the tool save manual work? | Batch CSV and JSON reports |
| 05 | Is its competitive position clear? | Offline redacted generic checks |
| 06 | Is the API bounded? | One URL and 5,000-run limit |
| 07 | Are results deterministic? | Pure check_url function |
| 08 | Do error codes enable automation? | Codes CLD001-201 |
| 09 | Does it preserve ordinary query filters? | Regression for duplicate tags |
| 10 | Does it handle malformed inputs? | Tests for scheme, host, encoding, controls |
| 11 | Does default output expose inputs? | No raw URL in checks |
| 12 | Can it leak network data? | No networking dependency |
| 13 | Does it refuse URL credentials? | Parser rejection |
| 14 | Are secret fields detected? | Heuristics, not complete |
| 15 | Can output still expose data? | Build/strip explicitly print URLs |
| 16 | Are compliance claims honest? | No certification claimed |
| 17 | Are product limitations stated? | No live link checking |
| 18 | Is the implementation original? | Authored for open-source release; rights review pending |
| 19 | Are partner/client policies excluded? | Generic web standards only |
| 20 | Is the public license clear? | MIT |
| 21 | Are three useful actions available? | Check, build, strip |
| 22 | Are safe batch workflows possible? | URL CSV/text and stdin |
| 23 | Are docs legible without visual UI? | Plain Markdown and help |
| 24 | Is access equitable and free? | Stdlib-only, R0 |
| 25 | Can failures be debugged safely? | Code + generic message |
| 26 | Are false positives attacked? | Duplicate generic tags preserved |
| 27 | Are there regression tests? | Python unittest suite |
| 28 | Is private vulnerability reporting documented? | SECURITY |
| 29 | Is community participation practical? | CONTRIBUTING and issue guidance |
| 30 | Did independent reviewers approve release? | **Hosted CI passed on initial commit. Founder authorized public alpha; external review still outstanding.** |

The product makes no claim of live platform validation, paid-media performance uplift, marketing-certification approval, 30 independent workers or achieved stars.


## Publication classification

Original, narrowly scoped open-source **alpha** authorized by the founder on 20 October 2026. Live production guarantees, external independent expert approvals, partnerships and star/adoption counts are **not** claimed. Re-run hosted checks on the final hardened commit before a public launch.

## Browser 30-Furies extension (2026-10-20)

The same 30 questions apply to the new browser surface. The 30 additional Node tests cover parsing, PII redaction, UTM building and stripping logic. The static app uses DOM `textContent`, not `innerHTML`, for user-controlled inputs; forbids third-party network connections with a restrictive CSP; and uses keyboard-operable ARIA tabs. These are **design measures and local tests only**, not a completed external security audit, browser E2E check or accessibility certification. Human visual QA and independent expert reviews remain outstanding.
