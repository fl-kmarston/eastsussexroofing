# East Sussex Roofing technical evidence

This directory contains a low-rate, passive public-site audit. Run it from Ubuntu with Python 3:

```sh
python3 scripts/collect_audit.py
```

The collector uses Python's standard library plus `curl`, `dig`, and `openssl`. It performs GET/HEAD requests only, stays same-origin for the crawl, waits approximately one second between page requests, and does not submit forms or authenticate.

The primary handoff is `East_Sussex_Roofing_Technical_Evidence.md`. Raw headers, DNS answers, TLS output, HTML excerpts, inventories, crawl data, rendered screenshots, and browser measurements are retained under `raw/`. Playwright uses a user-local Chromium runtime; Lighthouse, Axe, and field data still require separate tooling.

Target: `https://eastsussexroofing.co.uk/`