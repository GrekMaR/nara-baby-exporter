# nara-baby-exporter

Nara Baby & Pregnancy Tracker is moving to a **paid-only** model. This
repo is a small, safe, local tool to get **all your data out of Nara**
into an open, portable format — so you can keep your baby's history no
matter which app (or no app) you use next.

It does **not** scrape, reverse-engineer, or connect to Nara in any way.
Nara already provides an official CSV export; this tool just parses and
normalizes that CSV into a clean, app-agnostic schema (CSV + JSON).

## Why this exists: Nara's pricing change

Verified directly from Nara's own FAQ (`nara.com/pages/nara-baby-app-faqs`,
checked 2026-09-23) and corroborated by recent App Store reviews:

| | |
|---|---|
| **Monthly** | $9.99/month |
| **Lifetime** | $99.99 one-time |
| **Free trial** | 7 days, starts on your first logged activity, no card required |
| **Tiers** | None — both plans include every feature, no extra in-app purchases |
| **If you don't pay after the trial (or let a subscription lapse)** | The whole app family (you *and* every invited caregiver) goes **read-only**: you can still view and export existing data, but can't log anything new |
| **Promotions seen** | ~$6.99/month, ~$70–80 lifetime (occasional, not guaranteed) |

For context, other well-known baby trackers charge **$0–5/month** for
comparable core tracking (see [Alternatives](#alternatives) below) — so
$9.99/mo ($120/yr) or a forced $99.99 lifetime purchase for an app with
**no ads and no free tier at all** is a notably aggressive move for what
remains, at its core, a diaper/feeding/sleep logger.

This isn't a complaint about charging for software — it's that there's
**no non-paying way to keep using the app going forward**, which is why
exporting your history now, before you decide whether to pay, matters.

## What this tool does

1. You export your data from Nara yourself (official, built-in feature —
   see [`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md) for exact
   steps). This works even without a subscription.
2. This tool parses that CSV and normalizes it into:
   - `*.normalized.csv` — flat, one row per event, consistent units
   - `*.normalized.json` — same data, structured for programmatic reuse
3. You keep that output as a permanent, app-independent archive, and/or
   use it as a reference when re-entering data into a new app.

### Confirmed data coverage (v1)

Verified against a real, user-provided Nara export (692 rows, ~3 months
of a newborn's data): **breastfeeding, sleep, diaper changes, bottle
feeding, pumping, growth (weight/height/head size), and child profile
info** are all fully parsed and normalized.

Nara's app also supports solids, medications, vaccines, milestones,
routines, and pregnancy/postpartum tracking — these weren't present in
the sample export (a newborn hasn't used them yet), so they aren't
confirmed in CSV form yet. The parser **won't drop or crash on them** —
unrecognized rows are preserved as raw data — but they're not cleanly
typed. See [`schema/FIELD_MAPPING.md`](schema/FIELD_MAPPING.md) for exact
confidence levels per field, and please contribute a sample if you have
one of these categories.

**Not recoverable via CSV at all:** photos/attachments (back these up
separately from your camera roll before losing access).

## Quick start

Requires Python 3.10+.

```powershell
git clone https://github.com/GrekMaR/nara-baby-exporter.git
cd nara-baby-exporter
python -m venv .venv
.\.venv\Scripts\pip install -e .

# 1. See what's in your export
.\.venv\Scripts\python -m nara_exporter.cli summary path\to\your_export.csv

# 2. Convert it
.\.venv\Scripts\python -m nara_exporter.cli export path\to\your_export.csv --out-dir .\out
```

Full walkthrough (including how to get the export out of the Nara app in
the first place, and what to do once you have it): see
[`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md).

## Alternatives

A short, deliberately small list — all free or freemium (ads or a capped
free tier, not paywalled entirely), cross-platform (iOS + Android):

| App | Model | Good for |
|---|---|---|
| **[Baby Connect](https://apps.apple.com/us/app/baby-connect-newborn-tracker/id326574411)** | Freemium | Closest 1:1 feature match to Nara (feeding, diaper, sleep, growth, milestones, multi-caregiver sync) |
| **[Huckleberry](https://apps.apple.com/us/app/huckleberry-baby-tracker/id1169136078)** | Free core tracking, paid sleep-coaching add-on | Lightweight logging + well-regarded sleep prediction features |
| **[Glow Baby Tracker](https://apps.apple.com/us/app/glow-baby-tracker-growth-app/id1077177456)** | Free with optional premium | Growth charts and multi-child support |

None of these had a verified "bulk-import your Nara CSV" feature at time
of writing — see the honest caveat and per-app notes in
[`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md). Treat this tool's
output as your durable backup regardless of where you end up.

## Repository layout

```
src/nara_exporter/   CLI + parsing/normalization library (stdlib only, no dependencies)
schema/              Field mapping matrix, with confidence levels per field
docs/                Full migration guide
examples/            Synthetic sample export + expected shape (no real personal data)
tests/               Unit tests
```

## Contributing

If your Nara export contains an activity type not yet listed as
"Confirmed" in `schema/FIELD_MAPPING.md` (solids, medications, vaccines,
milestones, routines, pregnancy/postpartum tracking), please open an
issue or PR with the **raw header row and a redacted/synthetic sample
row** (no real names, dates, or personal notes) so the mapping can be
completed.

## License

MIT — see [`LICENSE`](LICENSE).

## Disclaimer

Not affiliated with Nara Organics, Inc. Pricing and feature information
was accurate as of 2026-09-23 per Nara's own published FAQ and may have
changed since — always verify current pricing/terms directly with Nara
before making a decision based on this README.
