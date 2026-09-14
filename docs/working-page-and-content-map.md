# East Sussex Roofing: Working Page and Content Map

Status: initial Eleventy content plan. Every factual field marked `VERIFY` must be confirmed by management before publication.

## Primary routes

| Route | Purpose | Content status |
|---|---|---|
| `/` | Homepage and quote conversion | Draft from approved positioning; VERIFY all business claims |
| `/roof-problems/` | Hub using customer language | Draft |
| `/roof-problems/leaking-roof/` | Explain symptoms, safe next steps, matching service | Draft; VERIFY process claims |
| `/roof-problems/missing-slipped-tiles/` | Customer problem route | Draft; VERIFY service scope |
| `/roof-problems/storm-damage/` | Customer problem route | Draft; VERIFY emergency wording |
| `/roof-problems/damp-and-ceiling-stains/` | Customer problem route | Draft; VERIFY diagnostic claims |
| `/roof-problems/flat-roof-problems/` | Customer problem route | Draft; VERIFY materials and scope |
| `/roof-problems/chimney-and-flashing-leaks/` | Customer problem route | Draft; VERIFY leadwork scope |
| `/roof-problems/gutter-overflow/` | Customer problem route | Draft; VERIFY gutter services |
| `/repair-services/` | Service hub | Draft |
| `/repair-services/roof-leak-repairs/` | Service detail | Draft; VERIFY guarantees/response times |
| `/repair-services/tile-and-slate-repairs/` | Service detail | Draft |
| `/repair-services/ridge-verge-valley-repairs/` | Service detail | Draft |
| `/repair-services/chimney-and-leadwork-repairs/` | Service detail | Draft |
| `/repair-services/flat-roof-repairs/` | Service detail | Draft |
| `/repair-services/guttering-fascias-soffits/` | Service detail | Draft |
| `/repair-services/roof-inspections/` | Service detail | Draft; VERIFY inspection deliverable |
| `/new-roofs/` | New roofs and re-roofing | Draft; VERIFY offering |
| `/projects/` | Curated evidence index | Needs approved project data |
| `/areas/` | Service-area hub | Draft; VERIFY coverage |
| `/areas/brighton-and-hove/` | Authoritative local hub | Draft; VERIFY neighbourhoods and evidence |
| `/about/` | Business identity and process | Needs management-approved facts |
| `/contact/` | Contact and quote route | Needs authoritative contact details |
| `/privacy/` | Privacy notice | Draft policy; mandatory management/legal review |
| `/cookies/` | Cookie information | Draft policy; mandatory management/legal review |
| `/accessibility/` | Accessibility statement | Draft operational statement; management review |
| `/terms/` | Website terms | Draft policy; mandatory management/legal review |
| `/404.html` | Helpful not-found route | Draft |

## Roof problem taxonomy

- Leaking roof / water ingress
- Missing, slipped, or broken tiles and slates
- Storm or wind damage
- Damp patches and ceiling stains
- Flat-roof cracking, bubbling, or standing water
- Chimney or flashing leaks
- Damaged ridges, verges, or valleys
- Overflowing or damaged gutters

## Repair service taxonomy

- Roof leak repairs
- Tile and slate repairs
- Ridge, verge, and valley repairs
- Chimney and leadwork repairs
- Flat-roof repairs
- Guttering, fascias, and soffits
- Roof inspections
- New roofs and re-roofing
- Emergency make-safe only if management confirms it is genuinely offered

## Project record shape

Each project should contain:

- `title`
- `location`
- `problem`
- `work`
- `outcome`
- `service`
- `images`
- `alt`
- `approved: true|false`
- `approval_note`

Do not publish customer names, addresses, reviews, guarantees, or before/after claims without permission and management approval.

## Global identity placeholders

- Business name: `East Sussex Roofing` VERIFY
- Primary phone: `VERIFY one authoritative number`
- Quote email: `quotes@eastsussexroofing.co.uk` VERIFY mailbox and routing before prominent use
- General email: `enquiries@eastsussexroofing.co.uk` VERIFY mailbox and routing before prominent use
- Current public Gmail: retain only during migration; VERIFY preferred display address
- Address: `VERIFY`
- Opening hours: `VERIFY`
- Service area: Brighton & Hove and genuine East Sussex coverage, VERIFY exact boundary
