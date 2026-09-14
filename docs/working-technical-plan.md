# East Sussex Roofing: Working Technical Plan

Status: build plan for the new Eleventy site.

## Reference implementation

Use `/home/keith/workspaces/massage-brighton` as the local reference for:

- Markdown content with front matter.
- `src/` input and `dist/` output.
- `_includes/` layouts and `_data/` site data.
- `static/` passthrough assets.
- Makefile build and local serving conventions.
- A small preprocessing layer rather than a large framework.

## Proposed project shape

```text
src/
  _data/site.js
  _includes/layouts/base.njk
  _includes/components/header.njk
  _includes/components/footer.njk
  _includes/components/cta.njk
  _includes/components/project-card.njk
  _includes/components/problem-card.njk
  _includes/components/service-card.njk
  pages/index.njk
  pages/roof-problems.njk
  pages/repair-services.njk
  pages/projects.njk
  pages/areas.njk
  pages/about.njk
  pages/contact.njk
  pages/policy.njk
  content/problems/*.md
  content/services/*.md
  content/projects/*.md
  content/pages/*.md
  static/css/site.css
  static/js/site.js
  static/images/
.eleventy.js
package.json
Makefile
.github/workflows/deploy.yml
```

## Build rules

- `npm run build`: Eleventy build from `src` to `dist`.
- `npm run serve`: local Eleventy server with `--serve`.
- `make build`: install-free local build after dependencies exist.
- `make serve`: build then serve `dist` on a documented local port.
- `make clean`: remove `dist` and generated caches.
- GitHub Actions: checkout, setup Node 20, `npm ci`, `npm run build`, upload `dist`, deploy GitHub Pages.
- Keep `node_modules/`, `dist/`, and local browser runtime/dependency artifacts out of git.

## Static behaviour

- No client-side framework.
- Small vanilla JS only for mobile menu, disclosure states, and accessible gallery/lightbox if required.
- No form submission endpoint is assumed. The form should use a clearly documented placeholder action or `mailto` only after management approves the delivery route. Never imply successful delivery without a tested endpoint.
- Use native lazy loading and responsive image attributes where assets are available.
- Add JSON-LD only from verified identity/content data; do not invent schema values.

## SEO and metadata

Every generated page needs a unique title, description, canonical URL, language, Open Graph title/description/image, one H1, descriptive internal links, and a useful 404. Generate sitemap and robots policy only after the production hostname and crawler policy are confirmed.

## Browser acceptance checks

Use the installed Python Playwright tool in `scripts/render_audit.py` as the regression baseline. Recheck:

- 320, 390, 430, 768, and 1440 CSS px.
- No horizontal overflow.
- Header height and primary CTA visibility.
- Menu keyboard operation and visible focus.
- Forms with labels, required state, and privacy wording.
- Gallery card size, `srcset`, lazy loading, captions, and keyboard viewer.
- Screenshot evidence for homepage, repair service, gallery, contact, and menu-open states.

The current live evidence reports overflow at 320 px for all sampled page types and gallery overflow at 768 and 1440 px. The new implementation must not reproduce those findings.
