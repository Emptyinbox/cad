# ctrl-alt-delete.ca

Static site for **Control Alt Delete** — managed IT services for small businesses across British Columbia and Alberta. Migrated from WordPress in May 2026; lives on GitHub Pages.

## Stack

- **Eleventy 3** as the static site generator
- **Vanilla CSS + Nunjucks templates** — no framework, no build step beyond Eleventy
- **GitHub Pages** for hosting, **GitHub Actions** for build & deploy
- **Formspree** for the contact form
- **Google Tag Manager** (`GTM-KRWCN6LR`) for analytics

## Local development

```bash
# One-time install
npm install

# Run with live reload at http://localhost:8080
npm run serve

# Production build to ./_site/
npm run build
```

## Editing content

Every page is a Markdown file under `src/`. Frontmatter sets the title, description, OG tags, and the layout. The body is regular Markdown.

Common edits:

- **Edit a service description** — `src/services/<slug>.md`
- **Edit a city's landing page** — `src/locations-served/<province>/<city>.md`
- **Edit an industry page** — `src/industries/<slug>.md`
- **Edit phone, email, social links** — `src/_data/site.json`
- **Add a city** — drop a new `.md` file in `src/locations-served/<province>/`, register it in `src/_data/locations.json`, push.
- **Add a blog post** — drop a `.md` file in `src/blog/posts/` with `layout: "layouts/blog_post.njk"` in frontmatter.

After editing, push to `main` — GitHub Actions builds and deploys automatically (~30 s).

## Project structure

```
.
├── .eleventy.js              # Eleventy config (collections, filters, passthrough)
├── package.json
├── CNAME                     # Custom domain — ctrl-alt-delete.ca
├── .github/workflows/
│   └── deploy.yml            # CI: build + push to GitHub Pages
├── scripts/
│   ├── extract_wp.py         # WP XML → Markdown (one-shot, used during migration)
│   └── download_media.py     # WP uploads → src/assets/img/
└── src/
    ├── _data/                # site.json, services.json, industries.json, locations.json
    ├── _includes/
    │   ├── layouts/          # base, page, home, service, industry, city, etc.
    │   └── partials/         # header, footer, cta, services-grid
    ├── assets/               # css, js, img — copied verbatim to /assets/ in output
    ├── index.md              # /
    ├── about.md              # /about/
    ├── contact-us.md         # /contact-us/
    ├── privacy-policy.md
    ├── blog/                 # blog index + posts
    ├── services/             # 8 services
    ├── industries/           # 13 industries + index
    ├── locations-served/     # 10 cities across BC + AB
    └── projects/             # email / cloud / server migrations
```

## Deploying

A push to `main` triggers `.github/workflows/deploy.yml` which:

1. Installs npm deps (cached)
2. Runs `npx @11ty/eleventy`
3. Publishes `_site/` as the GitHub Pages artifact

To enable Pages on a fresh repo: **Settings → Pages → Source: GitHub Actions**. Custom domain is read from the `CNAME` file at the repo root.

## DNS (Hover)

For the apex domain `ctrl-alt-delete.ca`:

| Type | Host | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | `<github-username>.github.io.` |

Wait for HTTPS cert provisioning (5–60 min after DNS resolves).

## License

Proprietary. All rights reserved.
