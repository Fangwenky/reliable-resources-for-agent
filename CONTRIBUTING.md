# Contributing

Welcome! This registry's entire value rests on **trust**, so its listing bar is higher than a typical awesome-list.

> 🌐 中文版：[CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md)

## Listing philosophy

Our bar is not just "is it real", but "is it worth listing". There is one core test: **has this product or project created real value for the internet and for many people's daily use?** If it has become a tool used by many, part of the internet's infrastructure, then listing it is a given — no matter whether it comes from a big company, an indie developer, or an open-source community.

The rules below are guidelines, not hard law — judge flexibly:

**Prefer**: long-lived projects with an open-internet spirit — open, maintained by a community or non-profit, where creators and users benefit directly. E.g. long-maintained open-source software, open knowledge bases, and other public-interest projects. This is the focus of the first batch.

**Infrastructure-level products**: widely used products that have become internet infrastructure should be listed regardless of who makes them. Company-owned products at this level are generally listed as `reference` (official address only, for anti-phishing, no endorsement); cases of clear broad public value may be `endorsed` at the maintainer's judgment. Big brands are exactly where phishing clones thrive, so reference listings must be clearly labeled "reference only".

**Promotion partnerships**: if a company wants its product promoted, they are welcome to reach out. Once it passes review, we list it and give it a featured spot on the website where human visitors can see it. Featured spots are clearly labeled as partnerships, separate from review-based listings. This is one of the project's future partnership and revenue directions.

**New products / indie developers / startups**: submissions are welcome, but listing requires enhanced manual review — verify the maker's identity, confirm official channels, assess sustainability and maintenance; re-check regularly after listing, and downgrade or delist on abandonment, deterioration, or loss of contact.

**Never**: middlemen that extract value through monopoly — sites that plagiarize or freely aggregate creators' content, build information monopolies, while the actual creators earn nothing. Judge by three questions:
- Do creators benefit directly (revenue share, attribution, traffic back)?
- Is there an open alternative (open source, open API, data portability)?
- Does it create lock-in rather than interoperability?

One-liner: if users are paying for a good service, list it; if they're forced to pay for a monopoly, don't.

## What you can contribute

- New trustworthy resource entries (fill in per `data/SCHEMA.md`)
- New/updated mirrors for existing resources (most needed when domains rotate)
- Report dead links and phishing clones (open an issue — no PR needed)

## Listing criteria (all required)

1. **Authenticity**: the resource genuinely exists with a clear official source.
2. **Evidence**: the `verification` field is complete, and `method` must be one of:
   - `official-domain`: a long-lived stable official domain
   - `official-announcement`: backed by an official channel (announcement page, official social account, official API returning domain lists, etc.) — the PR description must link the evidence or attach a screenshot
   - `community-consensus`: without official backing, requires maintainer testing + at least one independent cross-verification source
3. No `unverified` entries enter `main`.
4. **URL rules**: no short links, redirect links, or tracking-laden affiliate links.

## Anti-poisoning rules (for mirror PRs — the critical part)

This is the repo's core security red line, because the most motivated attacker behavior is "donating" a phishing site:

- A new mirror must state **its relationship to the official source** (official announcement / official account post / listed by official API — one of the three, with evidence linked).
- "It opens and looks like the official site" is **not** a listing reason — phishing sites can do that too.
- Maintainers independently re-verify mirrors (probe from a different network, check the TLS certificate subject, cross-check official channels).
- Gray-area resources (e.g. sites involving copyrighted content) must be marked `risk: gray-area` with the risk explained in the description; such PRs need explicit maintainer approval.

## Bilingual entries

Resource names and descriptions are bilingual: `name` / `description` (Chinese) and `name_en` / `description_en` (English). When adding an entry, please provide both; if you can only write one language, fill that one in and leave the other out — it falls back automatically. Evidence notes (`verification.evidence`, mirror `note`) may stay in the contributor's own language.

## PR process

1. Fork this repo and add/edit entries in `data/resources.yaml` per `data/SCHEMA.md`.
2. Run `python scripts/check_links.py --only <resource-id>` locally to confirm the URLs are reachable.
3. Open a PR describing: what was added/changed and what the verification evidence is (with links).
4. CI health-check passes + maintainer review passes → merged.

## Reporting issues

- Dead link: open an issue titled `[dead] <resource-id> - <dead-URL>`.
- Phishing clone found: open an issue titled `[phishing] <clone-domain>` with evidence (screenshot / technique description). Once confirmed it is recorded in the resource's `note` as a warning.
