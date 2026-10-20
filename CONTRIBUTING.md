# Contributing

Please report a reproducible, privacy-safe link fixture with the expected and actual code. No real campaign credentials, customer links, tracking identities or vendor-client confidential creative information in issues. General web-standards based improvements are welcome; do not copy platform-specific proprietary policy. New checks require a false-positive and false-negative test where possible.

Run:

~~~sh
python -m unittest discover -s tests -v
python -m campaign_link_doctor check --file examples/links.csv
~~~

Keep the default offline and redacted. Contributions are human reviewed and must be MIT-compatible. Never auto-merge externally supplied changes.

