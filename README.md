# Campaign Link Doctor

**Catch broken campaign tracking before someone spends money promoting the link.**

A free, local-first URL preflight for marketers, analysts, agencies, founders and developers. Audit UTM completeness, duplicate tracking tags, personal-data leaks, malformed URLs and clickable link identifiers. Then build consistent campaign URLs or strip tracking parameters.

No login, browser extension, telemetry, network request, API token or paid service.

## Start in 30 seconds

Requires Python 3.10 or newer. Everything runs with the Python standard library.

~~~sh
python -m campaign_link_doctor check "https://example.org/sale?utm_source=newsletter&utm_medium=email&utm_campaign=october"
~~~

Or install the command-line tool from the repository:

~~~sh
python -m pip install .
campaign-link-doctor --help
~~~

## Check links without echoing sensitive values

~~~sh
python -m campaign_link_doctor check "https://example.org/p?utm_source=partner"
python -m campaign_link_doctor check --file examples/links.csv --format json
python -m campaign_link_doctor check --file examples/links.txt --format csv
~~~

Check accepts URLs, a newline-delimited file, CSV with a url header, or --file - to read stdin. **Check reports only link index, counts and generic diagnostic messages.** Input URL values, tokens and domains are never echoed into a report. Do not put sensitive URLs directly in command arguments, where they may be visible in shell history or process listings. Use stdin instead.

Exit codes: 0 clean or warnings only, 1 errors (or warnings with --strict), 2 invalid arguments/input.

## Build consistent campaign tags

~~~sh
python -m campaign_link_doctor build --base "https://example.org/shop?sku=123" --source newsletter --medium email --campaign october
~~~

Build preserves non-campaign query parameters, encodes new values safely and refuses to duplicate UTMs unless you explicitly pass --replace. Build also refuses query parameters that appear to contain emails or sensitive keys. **Build deliberately prints the resulting URL**, unlike check.

## Clean links before sharing

~~~sh
python -m campaign_link_doctor strip "https://example.org/story?utm_source=mail&utm_medium=email&utm_campaign=news&fbclid=sample"
~~~

Strip removes known marketing click IDs, UTM values and query parameters suspected of containing email or secrets. It prints the cleaned link at your request and reports how many parameters were removed. **Always review the result:** removing a query parameter can change website behaviour, and sensitive information embedded in a URL path is not inspected by this first release.

## What gets caught

| Code | Meaning |
| --- | --- |
| CLD001 | Bad/missing URL, unsafe scheme, URL credentials or malformed encoding |
| CLD002 | Duplicate campaign or click-ID parameters |
| CLD003 | Potential personal data or credentials in a query |
| CLD004 | Empty campaign value |
| CLD101 | Non-HTTPS link |
| CLD102 | Inconsistent UTM casing or whitespace |
| CLD103 | Incomplete UTM source/medium/campaign combination |
| CLD104 | Campaign parameters appear in a fragment |
| CLD201 | Platform click identifier present, consider before sharing |

This is a **generic developer/marketing utility**, not copied advertising platform policy, no vendor endorsement, no customer targeting or internal campaign strategy.

## Boundaries

- No platform API integration or live destination/redirect validation.
- No guaranteed detection of all personal data or all link-breaking mistakes.
- CSV input is capped at 2 MiB; checks allow up to 5,000 URLs per run and 8,192 characters per URL.
- Queries can contain secrets in unusual names that the rule list misses. Default check never prints raw URLs.
- The code never accesses ad accounts and never makes web requests.

Run the 40-test suite:

~~~sh
python -m unittest discover -s tests -v
~~~

See [Contributing](CONTRIBUTING.md), [Security](SECURITY.md), [privacy model](docs/PRIVACY.md), and the [30-Furies review](docs/FURIES_30.md).

Made available by **Pryntor Open Source**, MIT licensed, forever free.

