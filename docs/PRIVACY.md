# Privacy model

The checker is a local-only parser. URLs and CSV data are never transmitted by this package, and no persistent logs are created by it. Generic diagnostic codes and counts contain no input URLs. The build and strip subcommands explicitly return a URL to the caller and are not redacted.

Threats still outside scope: shell command history, OS process argument logs, CI logs that echo the invoking command, malicious shells or environments, tracking and secrets encoded in URL paths/fragments, and personal data under unknown parameter names. Do not treat a clean lint report as a privacy certification. Use --file - for sensitive inputs and run in a trusted local environment.

