#!/usr/bin/env python3
"""Rendered, non-submitting browser checks for the public site."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "raw" / "screenshots"
RENDERED = ROOT / "raw" / "accessibility"
BASE = "https://eastsussexroofing.co.uk/"
PAGES = {
    "homepage": BASE,
    "roof-repair": BASE + "roof-repair/",
    "gallery": BASE + "gallery/",
    "contact": BASE + "contact/",
}
VIEWPORTS = {
    "320": (320, 800),
    "390": (390, 844),
    "430": (430, 932),
    "768": (768, 1024),
    "1440": (1440, 900),
}


def main() -> int:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    RENDERED.mkdir(parents=True, exist_ok=True)
    collected = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for page_name, url in PAGES.items():
            for viewport_name, (width, height) in VIEWPORTS.items():
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                try:
                  response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                except Exception:
                  response = None
                page.wait_for_timeout(500)
                page.evaluate("window.scrollTo(0, 0)")
                safe = f"{page_name}-{viewport_name}"
                screenshot_error = ""
                try:
                  page.screenshot(path=str(SCREENSHOTS / f"{safe}.png"), full_page=True, timeout=120000)
                except Exception as exc:
                  screenshot_error = repr(exc)
                record = page.evaluate("""() => {
                    const rect = el => { const r = el.getBoundingClientRect(); return {
                      x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height)
                    }; };
                    const text = document.body.innerText || '';
                    const links = [...document.querySelectorAll('a')].map(a => ({text: (a.innerText || '').trim(), href: a.href}));
                    const images = [...document.images].map(img => ({src: img.currentSrc || img.src, alt: img.alt,
                      naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight, rendered: rect(img),
                      loading: img.loading, width: img.getAttribute('width'), height: img.getAttribute('height'),
                      srcset: img.getAttribute('srcset') || ''}));
                    const forms = [...document.forms].map(form => ({action: form.action, method: form.method,
                      fields: [...form.elements].map(field => ({name: field.name, type: field.type, required: field.required,
                        autocomplete: field.autocomplete, label: field.labels?.[0]?.innerText || ''}))}));
                    const headings = [...document.querySelectorAll('h1,h2')].map(h => ({tag: h.tagName, text: h.innerText.trim()}));
                    const buttons = [...document.querySelectorAll('button,a,input,select,textarea')].map(el => ({
                      tag: el.tagName, text: (el.innerText || el.getAttribute('aria-label') || el.value || '').trim().slice(0, 120), rendered: rect(el)
                    }));
                    return {title: document.title, language: document.documentElement.lang, url: location.href,
                      viewport: {width: innerWidth, height: innerHeight}, documentWidth: document.documentElement.scrollWidth,
                      bodyWidth: document.body.scrollWidth, horizontalOverflow: document.documentElement.scrollWidth > innerWidth + 1,
                      h1: headings.filter(h => h.tag === 'H1'), h2Count: headings.filter(h => h.tag === 'H2').length,
                      headings, images, forms, links, buttons, wordCount: text.trim().split(/\\s+/).filter(Boolean).length,
                      metaDescription: document.querySelector('meta[name="description"]')?.content || '',
                      canonical: document.querySelector('link[rel="canonical"]')?.href || '',
                      header: document.querySelector('header') ? rect(document.querySelector('header')) : null,
                      bodyTextExcerpt: text.slice(0, 5000)};
                }""")
                records.append({"page": page_name, "requested": url, "status": response.status if response else None,
                                "viewportName": viewport_name, "screenshot": f"raw/screenshots/{safe}.png",
                                "screenshotError": screenshot_error, "data": record})
                page.close()
        browser.close()
    output = {"collected": collected, "tool": "Python Playwright", "records": records}
    (RENDERED / "rendered-audit.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())