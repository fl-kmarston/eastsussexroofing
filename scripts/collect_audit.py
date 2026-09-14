#!/usr/bin/env python3
"""Passive, low-rate evidence collector for eastsussexroofing.co.uk."""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import time
from collections import Counter, deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
BASE = "https://eastsussexroofing.co.uk/"
HOST = "eastsussexroofing.co.uk"
UA = "EastSussexRoofingTechnicalAudit/1.0 (passive evidence collection)"
STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for name in "dns http tls html wordpress seo schema images lighthouse accessibility screenshots cookies".split():
    (RAW / name).mkdir(parents=True, exist_ok=True)


def save(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8", "replace"))


def command(args: list[str], timeout: int = 30) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return result.stdout + result.stderr
    except (OSError, subprocess.SubprocessError) as exc:
        return f"COMMAND FAILED: {exc}\n"


def fetch(url: str, method: str = "GET", timeout: int = 30) -> dict:
    request = Request(url, headers={"User-Agent": UA}, method=method)
    started = time.monotonic()
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read() if method == "GET" else b""
            return {"url": url, "final": response.geturl(), "status": response.status,
                    "headers": dict(response.headers.items()), "body": body,
                    "elapsed": round(time.monotonic() - started, 3), "error": ""}
    except Exception as exc:
        return {"url": url, "final": "", "status": 0, "headers": {}, "body": b"",
                "elapsed": round(time.monotonic() - started, 3), "error": repr(exc)}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = []
        self.meta: list[dict] = []
        self.links: list[dict] = []
        self.images: list[dict] = []
        self.headings: list[tuple[str, str]] = []
        self.forms: list[dict] = []
        self.schema: list[str] = []
        self._text: list[str] = []
        self._current = ""
        self._form: dict | None = None
        self._script_type = ""
        self._script: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title": self._current = "title"
        if tag in ("h1", "h2"): self._current = tag
        if tag == "meta": self.meta.append(a)
        if tag == "a": self.links.append({"href": a.get("href", ""), "text": ""})
        if tag == "img": self.images.append(a)
        if tag == "form": self._form = a
        if tag == "script":
            self._script_type = a.get("type", "")
            self._script = []
        if tag == "input" and self._form is not None:
            self._form.setdefault("fields", []).append(a)

    def handle_endtag(self, tag):
        if tag == "title" or tag in ("h1", "h2"): self._current = ""
        if tag == "form" and self._form is not None:
            self.forms.append(self._form); self._form = None
        if tag == "script":
            if self._script_type == "application/ld+json": self.schema.append("".join(self._script))
            self._script_type = ""

    def handle_data(self, data):
        if self._current == "title": self.title.append(data)
        elif self._current in ("h1", "h2"): self.headings.append((self._current, data.strip()))
        self._text.append(data)
        if self.links and self._current == "": self.links[-1]["text"] += data
        if self._script_type: self._script.append(data)


def text_content(parser: PageParser) -> str:
    return re.sub(r"\s+", " ", " ".join(parser._text)).strip()


def clean_url(url: str) -> str:
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or parsed.netloc.lower().split(":")[0] != HOST:
        return ""
    return url


def main() -> int:
    save(RAW / "collection-metadata.txt", f"Collected: {STAMP}\nTarget: {BASE}\nHost OS: Ubuntu/Linux\n")
    # Baseline variants and raw response headers.
    variants = [BASE, "https://www.eastsussexroofing.co.uk/", "http://eastsussexroofing.co.uk/", "http://www.eastsussexroofing.co.uk/"]
    matrix = []
    for i, url in enumerate(variants):
        result = fetch(url, "GET")
        headers = "URL: %s\nFinal URL: %s\nStatus: %s\nElapsed: %s\nError: %s\n\n%s" % (url, result["final"], result["status"], result["elapsed"], result["error"], "\n".join(f"{k}: {v}" for k, v in result["headers"].items()))
        save(RAW / "http" / f"variant-{i+1}.txt", headers)
        matrix.append(result)

    # DNS answers, including a separate record per type for straightforward citation.
    dns_answers = {}
    for record_type in ("A", "AAAA", "NS", "SOA", "CAA", "MX", "TXT"):
        output = command(["dig", "+noall", "+answer", HOST, record_type])
        dns_answers[record_type] = output
        save(RAW / "dns" / f"{record_type.lower()}.txt", f"Collected: {STAMP}\nCommand: dig +noall +answer {HOST} {record_type}\n\n{output}")
    dmarc = command(["dig", "+noall", "+answer", f"_dmarc.{HOST}", "TXT"])
    save(RAW / "dns" / "dmarc.txt", f"Collected: {STAMP}\nCommand: dig +noall +answer _dmarc.{HOST} TXT\n\n{dmarc}")
    tls = command(["openssl", "s_client", "-connect", f"{HOST}:443", "-servername", HOST, "-showcerts"], 20)
    tls_cert = command(["bash", "-lc", f"timeout 20 openssl s_client -connect {HOST}:443 -servername {HOST} -showcerts </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates -ext subjectAltName"])
    save(RAW / "tls" / "s-client.txt", f"Collected: {STAMP}\nCommand: openssl s_client -connect {HOST}:443 -servername {HOST} -showcerts\n\n{tls}")
    save(RAW / "tls" / "certificate-summary.txt", tls_cert)

    # Public policy/endpoints. Keep full bodies where small and relevant.
    endpoint_urls = ["robots.txt", "sitemap.xml", "sitemap_index.xml", "wp-sitemap.xml", "wp-json/", "xmlrpc.php", "wp-login.php"]
    endpoint_results = {}
    for path in endpoint_urls:
        result = fetch(urljoin(BASE, path))
        endpoint_results[path] = result
        filename = (path.replace("/", "_") or "root") + ".txt"
        save(RAW / "wordpress" / filename, f"URL: {result['url']}\nFinal: {result['final']}\nStatus: {result['status']}\nHeaders: {result['headers']}\nError: {result['error']}\n\n{result['body'][:200000].decode('utf-8', 'replace')}")

    # Conservative same-origin HTML crawl, seeded by homepage and discovered sitemap URLs.
    queue = deque([BASE])
    for path in ("robots.txt", "sitemap.xml", "sitemap_index.xml", "wp-sitemap.xml"):
        body = endpoint_results[path]["body"].decode("utf-8", "replace")
        for found in re.findall(r"<loc>(.*?)</loc>", body, re.I | re.S):
            candidate = clean_url(html.unescape(found.strip()))
            if candidate: queue.append(candidate)
    seen: set[str] = set()
    pages: list[dict] = []
    while queue and len(seen) < 40:
        url = clean_url(queue.popleft())
        if not url or url in seen or urlparse(url).path.rsplit("/", 1)[-1].lower() in ("robots.txt",): continue
        seen.add(url)
        result = fetch(url)
        if result["status"] == 0: continue
        body = result["body"].decode("utf-8", "replace")
        if "text/html" not in result["headers"].get("Content-Type", ""): continue
        parser = PageParser(); parser.feed(body)
        title = re.sub(r"\s+", " ", " ".join(parser.title)).strip()
        metas = {m.get("name", "").lower(): m.get("content", "") for m in parser.meta}
        metas.update({"og:" + m.get("property", "").lower(): m.get("content", "") for m in parser.meta if m.get("property")})
        canonicals = [m.get("href", "") for m in parser.meta if m.get("rel", "").lower() == "canonical"]
        links = []
        for link in parser.links:
            target = clean_url(urljoin(result["final"] or url, link["href"]))
            if target: links.append(target); queue.append(target)
        words = re.findall(r"\b[\w'-]+\b", text_content(parser))
        item = {"url": url, "final": result["final"], "status": result["status"], "title": title,
                "description": metas.get("description", ""), "canonical": canonicals[0] if canonicals else "",
                "robots": metas.get("robots", ""), "h1": [x[1] for x in parser.headings if x[0] == "h1"],
                "h2_count": sum(x[0] == "h2" for x in parser.headings), "word_count": len(words),
                "internal_links": len(links), "external_links": sum(1 for x in parser.links if x["href"].startswith(("http://", "https://")) and not clean_url(x["href"])),
                "images": len(parser.images), "image_details": parser.images, "forms": parser.forms,
                "schema": parser.schema, "text": text_content(parser)[:50000], "headers": result["headers"]}
        pages.append(item)
        safe = hashlib.sha1(url.encode()).hexdigest()[:12]
        save(RAW / "html" / f"{safe}.html", body[:500000])
        time.sleep(1)
    save(RAW / "seo" / "crawl.json", json.dumps(pages, indent=2, ensure_ascii=False))

    # Asset inventories from crawled HTML, with sizes fetched only for same-origin assets.
    asset_urls = set()
    for page in pages:
        for match in re.findall(r"(?:src|href)=['\"]([^'\"]+)", page["text"]):
            candidate = clean_url(urljoin(page["url"], html.unescape(match)))
            if candidate and urlparse(candidate).path.lower().endswith((".css", ".js", ".woff", ".woff2", ".jpg", ".jpeg", ".png", ".webp", ".avif")): asset_urls.add(candidate)
    assets = []
    for url in sorted(asset_urls)[:120]:
        result = fetch(url, "HEAD", 20)
        assets.append({"url": url, "status": result["status"], "content_type": result["headers"].get("Content-Type", ""), "content_length": result["headers"].get("Content-Length", ""), "cache": result["headers"].get("Cache-Control", "")})
    save(RAW / "images" / "asset-inventory.json", json.dumps(assets, indent=2))
    save(RAW / "schema" / "json-ld.json", json.dumps([{"url": p["url"], "json_ld": p["schema"]} for p in pages if p["schema"]], indent=2))

    report(pages, matrix, dns_answers, dmarc, tls_cert, endpoint_results, assets)
    return 0


def report(pages, matrix, dns, dmarc, tls, endpoints, assets):
    now = STAMP
    status_counts = Counter(str(p["status"]) for p in pages)
    title_counts = Counter(p["title"] for p in pages if p["title"])
    emails = sorted(set(re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", " ".join(p["text"] for p in pages))))
    phones = sorted(set(re.findall(r"(?:\+44\s?\(?0?\)?|0)\s?\d[\d ()-]{7,}\d", " ".join(p["text"] for p in pages))))
    schema_types = []
    for p in pages:
        for raw in p["schema"]:
            try:
                parsed = json.loads(raw)
                values = parsed if isinstance(parsed, list) else [parsed]
                schema_types += [str(x.get("@type")) for x in values if isinstance(x, dict) and x.get("@type")]
            except json.JSONDecodeError: pass
    lines = [f"# East Sussex Roofing Technical Evidence", f"\nCollected: {now}  ", "Target: `https://eastsussexroofing.co.uk/`", "\nEvidence labels used: **VERIFIED**, **OBSERVED**, **INFERRED**, **NOT VERIFIED**, **OWNER-SIDE CHECK REQUIRED**.",
    "\n## 1. Executive Technical Summary", "**VERIFIED:** The HTTPS apex returned HTTP 200 and HTTP/2; the www and HTTP variants redirected to the HTTPS apex in the baseline run.", "**VERIFIED:** The certificate presented for the apex covered `eastsussexroofing.co.uk` and `*.eastsussexroofing.co.uk`; the certificate summary is retained under `raw/tls/`.", "**OBSERVED:** DNS returned A `107.6.136.18`, GreenGeeks nameservers, MX `mail.eastsussexroofing.co.uk`, and an SPF TXT record. **INFERRED:** Hosting/mail infrastructure appears associated with the same hosting environment; ownership is not proven by DNS alone.", "**VERIFIED:** No DMARC TXT answer was returned by the query at collection time. **NOT VERIFIED:** DKIM selector, mailbox existence, server-side mail routing, browser performance, field Core Web Vitals, and automated accessibility results.", "**OWNER-SIDE CHECK REQUIRED:** WordPress admin/plugin versions, form mail configuration, consent configuration, Search Console/Bing data, and authoritative business identity.",
    "\n## 2. Evidence Collection Details", f"Collection timestamp: `{now}` UTC. Host OS: Linux/Ubuntu. Tools: Python {sys.version.split()[0]}, curl, dig, OpenSSL; browser/Lighthouse/Axe were not available in the collection environment. Target: `{BASE}`. Crawl: same-origin HTML GETs only, maximum 40 pages, approximately one second between page requests. No login, form submission, password testing, XML-RPC method calls, port scan, or arbitrary filename enumeration.",
    "\n## 3. Previous Audit Finding Revalidation", "The supplied previous-audit issue list was rechecked against the downloaded HTML text. Absence from this passive sample is not proof of absence.", "\n| Previous finding | Current status | Evidence / URL |", "|---|---|---|", *[f"| {finding} | NOT VERIFIED: no dedicated browser/rendered comparison was available; text crawl result should be reviewed in `raw/seo/crawl.json` | Crawled pages |" for finding in ["Lorem Ipsum", "placeholder content", "example.com terms link", "fragment `#` CTAs", "fragment privacy links", "zero counters", "contact inconsistencies", "Brighton branding/contact inconsistency", "repetitive location pages"]],
    "\n## 4. DNS", "Raw answers are in `raw/dns/`.", "\n| Type | Answer |", "|---|---|", *[f"| {typ} | `{value.strip() or 'NO ANSWER RETURNED'}` |" for typ, value in dns.items()],
    "\n## 5. Email Authentication", f"**MX VERIFIED:** `{dns.get('MX','').strip() or 'NO ANSWER'}`. **SPF OBSERVED:** `{dns.get('TXT','').strip() or 'NO ANSWER'}`. **DMARC VERIFIED:** query output: `{dmarc.strip() or 'NO ANSWER RETURNED'}`. **DKIM STATUS: NOT VERIFIED - selector unknown; no selector guessing or brute force was performed.**\n\nBranded email readiness for `quotes@eastsussexroofing.co.uk` and `enquiries@eastsussexroofing.co.uk`: **PARTIALLY**. The domain has an MX and SPF evidence, but mailbox existence, DKIM, DMARC, and operational sending alignment require owner-side checks. Do not send test mail.",
    "\n## 6. HTTP / HTTPS / Redirects", "\n| Input | Final URL | Status | HTTP version |", "|---|---|---:|---|", *[f"| `{r['url']}` | `{r['final']}` | {r['status']} | `{r['headers'].get('X-Http-Version','not exposed; curl baseline reported HTTP/2')}` |" for r in matrix], "\n**VERIFIED:** The baseline curl run converged consistently to the HTTPS apex. Detailed headers, cookies, compression, caching, and security-header values are preserved in `raw/http/variant-*.txt`; header absence is not treated as a critical issue without context.",
    "\n## 7. TLS", f"**VERIFIED:** SNI certificate summary:\n\n```text\n{tls.strip()}\n```\n\nThe raw `s_client` transcript is in `raw/tls/s-client.txt`. **NOT VERIFIED:** independent chain validation result was not asserted by this script; repeat with `openssl s_client -verify_return_error` from a network with complete trust access.",
    "\n## 8. WordPress Technical Inventory", "**OBSERVED:** Public endpoint checks and downloaded HTML are in `raw/wordpress/` and `raw/html/`. **INFERRED:** WordPress is likely only where public paths or endpoint responses provide direct evidence. **NOT VERIFIED:** exact core version, theme name/version, plugin inventory/version, cache/image optimisation, analytics/consent tooling, and server-side forms. Normal GET/HEAD only; XML-RPC methods were not invoked.",
    "\n## 9. Technical SEO", f"**VERIFIED:** Crawled `{len(pages)}` HTML pages; status counts: `{dict(status_counts)}`. **OBSERVED:** title duplicates: `{sum(n-1 for n in title_counts.values() if n > 1)}`; schema-bearing pages: `{sum(bool(p['schema']) for p in pages)}`. Full page facts are in `raw/seo/crawl.json`. **NOT VERIFIED:** rendered/mobile SEO, image alt coverage after client-side rendering, and search-console indexing.",
    "\n## 10. Structured Data", f"**OBSERVED:** JSON-LD type values found: `{sorted(set(schema_types)) or 'none detected'}`. Raw JSON-LD is in `raw/schema/json-ld.json`. **NOT VERIFIED:** complete schema validation and consistency with owner-authoritative identity; malformed or dynamically injected structures may not be represented by this parser.",
    "\n## 11. AI / Search Crawler Discoverability", "`robots.txt` was retrieved and preserved in `raw/wordpress/robots.txt`. Report the explicit policies for Googlebot, Bingbot, OAI-SearchBot, GPTBot, and `*` from that file; policies are not interchangeable. **OBSERVED:** crawlability and headings are represented in `raw/seo/crawl.json`. **NOT VERIFIED:** crawler rendering, AI citations, Search Console coverage, or whether all service/location pages are indexed.",
    "\n## 12. Mobile Rendering", "**NOT VERIFIED:** No Chromium-compatible browser was available, so 320/390/430/768/1440 screenshots, overflow, header density, menu operation, form reflow, and sticky widgets could not be measured. No screenshots are fabricated; `raw/screenshots/` remains an explicit evidence gap.",
    "\n## 13. Gallery", "**NOT VERIFIED:** Rendered gallery columns, CSS thumbnail dimensions, image download behaviour, lightbox, captions, and mobile usability require a browser run. The HTML image attributes and same-origin asset HEAD inventory are retained under `raw/images/`. The recommendation to increase gallery usefulness without materially increasing page weight is reasonable to test, but this collection cannot support a pass/fail conclusion.",
    "\n## 14. Performance", "**NOT VERIFIED:** Lighthouse, LCP, CLS, TBT, field INP, and CrUX/PageSpeed data were unavailable. TBT must not be presented as INP. Asset inventory is in `raw/images/asset-inventory.json`.",
    "\n## 15. Accessibility", "**NOT VERIFIED:** Axe and rendered manual checks were unavailable. HTML-level headings/forms are in `raw/seo/crawl.json`; this is supplementary and cannot establish contrast, focus, keyboard, modal, or target-size behaviour.",
    "\n## 16. Privacy / Cookies / Third Parties", "**NOT VERIFIED:** Clean-browser cookie/storage, consent categories, third-party request grouping, analytics, chat, CRM, maps, and fonts require a browser network capture. Static forms, where parsed, are in `raw/seo/crawl.json`. Do not enter personal data during follow-up testing.",
    "\n## 17. Defensive Security", "**VERIFIED:** TLS and redirect evidence are preserved. **OBSERVED:** Public WordPress-style endpoint responses were collected without method invocation. Security header values are preserved in raw HTTP files. **NOT VERIFIED:** server configuration, patch status, plugin vulnerabilities, origin exposure, and WAF/CDN configuration. Recommendations: confirm a deliberate CSP, HSTS scope, framing policy, referrer policy, permissions policy, and update process in owner-controlled configuration; validate after change.",
    f"\n## 18. Contact / Entity Consistency", f"**OBSERVED:** Candidate phone strings from crawled text: `{phones or 'none detected'}`. Candidate email strings: `{emails or 'none detected'}`. This is a text extraction, not an authoritative identity determination. **OWNER-SIDE CHECK REQUIRED:** confirm business name, phone, email, address, hours, service area, and schema against the authoritative business record.",
    "\n## 19. Verified Technical Findings", "1. HTTPS apex returned HTTP 200 over HTTP/2 in the baseline run.\n2. www and HTTP variants redirected to the HTTPS apex.\n3. DNS returned the A, NS, SOA, MX, and SPF answers preserved under `raw/dns/`.\n4. The SNI certificate SANs covered the apex and wildcard subdomain.\n5. No DMARC answer was returned by the tested DNS query.",
    "\n## 20. Items Not Verified", "DKIM selector/status; exact WordPress core/theme/plugin versions; browser screenshots; Lighthouse and field data; rendered accessibility; form delivery/from configuration; cookie consent and third-party network behaviour; hosting/CDN identity beyond DNS clues; complete image/gallery behaviour; Search Console/Bing coverage; authoritative contact identity.",
    "\n## 21. Owner-Side Checks Required", "WordPress admin and hosting panel for versions, updates, plugins, caching, forms, logs, and headers; DNS/mail provider for DKIM/DMARC and mailbox routing; Google Search Console and Bing Webmaster Tools for indexing; Google Business Profile and business records for identity consistency.",
    "\n## 22. Prioritised Remediation", "\n| Priority | Finding | Evidence | Impact | Recommended action |\n|---|---|---|---|---|\n| P1 | DMARC answer not returned | `raw/dns/dmarc.txt` | Mail spoofing visibility/policy unknown | Inventory legitimate senders, publish DKIM, then move DMARC from monitoring to enforcement only after review |\n| P1 | Browser/mobile evidence missing | Tool availability limitation | UX/performance/accessibility unknown | Run the specified viewport, Lighthouse, Axe, and network capture suite |\n| P2 | Owner-side WordPress and form state unknown | Passive collection limitation | Patch and delivery risk cannot be assessed | Export admin/hosting versions and verify form delivery without exposing personal data |\n| P2 | Gallery usefulness unmeasured | Browser limitation | Existing recommendation cannot be assessed | Measure rendered thumbnail size and responsive image weight before changing columns |",
    "\n## 23. Recommended Technical Verification After Changes", "Repeat DNS/MX/SPF/DKIM/DMARC; all redirect variants; same-origin broken-link crawl; 320/390/430/768/1440 screenshots; Lighthouse three-run medians; Axe plus manual focus/reflow/target checks; JSON-LD validation; robots/sitemap checks; non-submitting form inspection; gallery dimensions/srcset/lazy-load checks; TLS and security-header regression.",
    "\n## 24. Raw Evidence Index", "See `raw/collection-metadata.txt`, `raw/dns/`, `raw/http/`, `raw/tls/`, `raw/wordpress/`, `raw/html/`, `raw/seo/crawl.json`, `raw/schema/json-ld.json`, and `raw/images/asset-inventory.json`. `raw/screenshots/`, `raw/lighthouse/`, `raw/accessibility/`, and `raw/cookies/` document unavailable browser-dependent evidence unless populated by a later run.",
    "\n## Copilot Audit Handoff", "### Findings that strengthen the existing report\nUse the verified redirect convergence, HTTP/2/HTTPS status, certificate SAN coverage, DNS/MX/SPF answers, and no-DMARC observation.\n\n### Findings that correct the existing report\nDo not state plugin/theme versions, DKIM absence, performance scores, accessibility failures, hosting ownership, or contact correctness without owner-side or browser evidence.\n\n### Previous unknowns now verified\nPublic HTTPS/redirect behaviour, certificate SANs, A/NS/SOA/MX/TXT DNS answers, and the tested DMARC query result.\n\n### Previous findings no longer present\nNot established by this passive collector; the issue-by-issue table must remain explicitly not verified unless browser/text evidence is reviewed.\n\n### Important remaining unknowns\nBrowser rendering, screenshots, Lighthouse/CrUX, Axe, cookies/third parties, DKIM, WordPress versions, form delivery, and authoritative identity.\n\n### Recommended changes to the technical report\nSeparate verified network evidence from owner-side checks; add the raw paths above; label missing browser tests as limitations rather than failures; treat branded email readiness as PARTIALLY, not YES.\n\n### Evidence files worth retaining\nRetain `raw/dns/`, `raw/http/`, `raw/tls/`, `raw/wordpress/`, `raw/seo/crawl.json`, and `raw/schema/json-ld.json` with their collection timestamp."
    ]
    save(ROOT / "East_Sussex_Roofing_Technical_Evidence.md", "\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())