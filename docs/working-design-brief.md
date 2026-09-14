# East Sussex Roofing: Working Design Brief

Status: implementation working notes. Source: `East_Sussex_Roofing_Web_Design_Management_Report 1.docx`, technical evidence, and rendered Playwright checks.

## Direction

Keep the existing East Sussex Roofing identity and white-on-black van branding as the visual foundation. This is a hierarchy and trust redesign, not a full rebrand. Change branding only where contrast, readability, keyboard access, target size, or mobile reflow requires it.

The primary customer route is:

1. Recognise a roof problem.
2. Find the matching repair service.
3. See genuine local project evidence.
4. Call or request a quote.

## Visual language

- Strong black/charcoal foundation with white type and restrained warm accent drawn from the existing roofing/van identity.
- Use high-contrast surfaces and avoid grey-on-black, thin type over photographs, and decorative text effects.
- Use an expressive display face only for major headings; use a highly readable sans-serif for navigation, body copy, forms, and metadata.
- Use real roofing imagery as evidence, not generic stock imagery.
- Keep cards square or lightly rounded, with clear borders and generous spacing.
- Use descriptive CTA labels: `View roof leak repairs`, `See flat-roof projects`, `Request a roof inspection`.
- Use familiar icons only when they improve scanning; never make an icon carry essential meaning without a text label.

## Header

Desktop navigation:

`Roof Problems` | `Repair Services` | `Projects` | `Areas` | `About` | `Get a Quote`

Mobile header:

`Logo` | `Call` | `Get a Quote` | `Menu`

Move the full email, address, and secondary phone details into the menu/footer. The live rendered audit found a 320 px overflow on homepage, repair, gallery, and contact pages, so the new header must be tested at 320, 390, and 430 CSS px and at 200% zoom.

## Homepage composition

1. Compact utility strip with one primary phone and service area.
2. Hero: `Roof Repairs in Brighton & Hove` plus one factual supporting sentence, `Call`, and `Get a Quote`.
3. Customer-recognised roof problems: six to eight cards.
4. Repair services: concise cards with direct routes.
5. Recent projects: three or four cards with location, problem, work completed, and outcome.
6. Why East Sussex Roofing: verified facts only.
7. Areas covered: Brighton & Hove first, then genuine East Sussex coverage.
8. Quote section with visible privacy wording.
9. Short footer with consistent identity, contact details, policies, and navigation.

## Accessibility acceptance criteria

- No horizontal scroll at 320 CSS px.
- Visible keyboard focus for every interactive control.
- Logical heading hierarchy and one useful H1 per page.
- Descriptive link and button labels.
- Persistent labels and clear errors in forms.
- Tap targets comfortably larger than 24 x 24 CSS px, with priority controls larger where practical.
- Useful alt text for project images; decorative images use empty alt.
- Sufficient contrast on every text/image combination.
- Menu and gallery/lightbox usable without a pointer.
- Test at 320, 390, 430, 768, 1440, and 200% zoom.

## Content boundary

Do not publish guarantees, response times, reviews, project claims, service areas, or technical credentials until management verifies them. Avoid creating a page for every problem x roof type x town combination. Prefer fewer strong pages with real evidence.
