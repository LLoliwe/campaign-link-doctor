# Zero-upload browser edition

The web interface runs entirely on your machine, in the browser. It is a no-account interface for the same general campaign-link lint rules as the Python CLI. No cloud processing, tracking, analytics, local storage, remote fonts or CDN dependencies.

## Get started

From the repository root:

~~~sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory web
~~~

Open http://127.0.0.1:8080 in your browser. This local server only serves static assets on your computer. Python and Node are **not** needed by visitors if someone serves the files via a static host. JavaScript modules may not work directly with a `file://` URL.

Run offline test suites:

~~~sh
node --test web/tests/*.test.mjs
python3 -m unittest discover -s tests -v
~~~

Features: check multiple links, build correctly escaped UTM links, clean tracking parameters, copy resulting links, keyboard-accessible tabs and mobile layout.

## Privacy and trust

- Only local browser JavaScript: no network requests and no analytics.
- Input URLs are **never** rendered in checker results (only index, number of parameters and generic finding codes).
- Build and clean intentionally display the resulting URL for explicit user use.
- The browser toolbar, operating system, extensions and browsing environment are outside our control.
- JavaScript rules and Python rules are independently tested but not guaranteed identical in every edge case.
- This is an alpha; no third-party security audit, screen-reader audit, real-browser automation, or analytics uplift is claimed.

The [30-Furies adversarial review](../docs/FURIES_30.md) applies to all browser changes.

