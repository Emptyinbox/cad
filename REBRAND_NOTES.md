# Rebrand & build-out — 2026-06-05

Applied the Tortoise & Hare "How Most MSP Websites Read" playbook (Todoist task "Add this to Website") plus the CAD cherry/charcoal brand system (`/cad-branding` skill).

## What changed

1. **Brand system** — site now uses the official CAD identity: cherry `#D72638` accent, charcoal `#1D1D1F` ink, white surfaces, hairline rules, pill buttons, Bricolage Grotesque headings + Plus Jakarta Sans body. The official SVG wordmark (both cherry braces) replaces the old PNG logo in header and footer. Old slate/sky palette fully removed.
2. **Transparent pricing** — new `/pricing/` page + pricing teaser band on home + nav link. Per the newsletter: ballpark ranges with lower/upper bounds and what moves the number.
3. **Outcomes band** on home — concrete measurables instead of vague promises.
4. **Case studies** — the 3 project pages now open with an outcome-driven case-study card; teaser cards embedded on managed-it-support, server-support, and cloud-computing-services.
5. **CTA rewritten** — "what happens next" 3-step strip (15-min call → plain-language assessment + ballpark → fixed written quote) on every page footer CTA.
6. Removed a "24/7" support phrasing on server-support (per cad-service-facts: no 24/7 on-call claims).

## ⚠️ Numbers to verify before cutover

Everything below is a credible placeholder, marked in source with `data-verify` attributes / `<!-- VERIFY -->` comments. Search the repo for `data-verify`.

| Where | Claim | Status |
|---|---|---|
| /pricing/ + home | Managed IT $110–$225/user/mo | $110 lower bound confirmed by James 2026-06-06; upper bound still estimate |
| /pricing/ + home | Security add-on $15–$45/user/mo | market-typical estimate |
| /pricing/, project pages | Email migration $2,500–$7,500 | estimate |
| /pricing/, project pages | Server migration $5,000–$15,000 | estimate |
| /pricing/ + home | $145/hr professional services | REAL — from standard quote terms |
| home outcomes | 1,400+ threats blocked monthly | placeholder |
| home outcomes | 38% fewer tickets after 90 days | placeholder |
| home outcomes | 15 min average first response | matches existing managed-it-support page claim — confirm |
| home outcomes | 99.9% backup restore success | placeholder |
| case studies (3) | All client metrics + anonymized client descriptions | placeholder — swap in real client stories |

## Build

Verified locally with Eleventy 3.1.5: 48 pages, no broken internal links. Push to `main` and the GitHub Action deploys to staging (emptyinbox.github.io/cad/).
