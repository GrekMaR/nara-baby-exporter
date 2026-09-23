# Migration Guide: Leaving Nara Baby for Another Tracker

## 1. Export your data from Nara (do this before your trial/subscription lapses)

Confirmed steps (from Nara's own FAQ, `nara.com/pages/nara-baby-app-faqs`):

1. Open the Nara app and go to the main **Activity** screen.
2. Tap the **avatar icon** next to your child's name.
3. Tap **Export Data**. This saves a CSV file for that child.
4. Repeat per child if you're tracking more than one (export is per-child).

This works even if you never subscribe, and continues to work after your
account goes read-only (i.e. after the 7-day trial ends without paying, or
after a subscription lapses) — per Nara's FAQ: *"You can still view and
export everything you logged... you can't add new entries until you sign
up."*

**Do this soon.** Nara doesn't currently promise indefinite data retention
for non-paying/read-only accounts, and app policies can change.

## 2. Normalize it with this tool

```powershell
# one-time setup
python -m venv .venv
.\.venv\Scripts\pip install -e .

# see what's in your export before converting
.\.venv\Scripts\python -m nara_exporter.cli summary path\to\export_narababy_<child>_<date>.csv

# convert to normalized CSV + JSON
.\.venv\Scripts\python -m nara_exporter.cli export path\to\export_narababy_<child>_<date>.csv --out-dir .\out
```

This produces `<name>.normalized.csv` and `<name>.normalized.json` — a
flat, app-agnostic record of every event, with consistent units (mL, kg,
cm) regardless of what unit Nara originally used. Keep these files as your
permanent historical archive regardless of which app you move to next.

If the summary command warns about unmapped activity types (e.g. you've
logged solids, medications, vaccines, or milestones — none of which
appeared in the sample export this tool was built from), the raw data for
those rows is still preserved in the JSON output's `raw_fields`, just not
broken into typed columns yet. See `schema/FIELD_MAPPING.md`.

## 3. Getting data into a new app

**Important, honest caveat:** most consumer baby-tracking apps are built
for day-to-day logging, not bulk historical import, and none of the three
apps below have a verified, up-to-date "import a CSV of past Nara data"
flow confirmed as part of this project's research. Import features change
often and vary by platform (iOS/Android) and plan. Before relying on any
specific import path:

- Check the target app's current help center/FAQ yourself for "import"
  or "switch from another app."
- Treat the normalized CSV/JSON from step 2 as your durable backup either
  way — even if you end up re-entering current/ongoing data by hand in
  the new app, you won't lose your Nara history.

With that caveat, here's the realistic migration approach for each
shortlisted app:

### Baby Connect
Historically the most feature-complete alternative and the closest 1:1
replacement for Nara's breadth (feeding, diaper, sleep, growth, milestones,
multi-caregiver sync). Some editions have offered a data-import path for
switching from another tracker in the past — verify current availability
in-app before assuming it exists. At minimum, its category set maps
cleanly onto this tool's normalized schema, so manual/bulk entry mapping
is straightforward if automated import isn't available.

### Huckleberry
Free tier covers core tracking (sleep, feeding, diaper); its well-known
paid feature is AI-driven sleep predictions/coaching. No confirmed bulk
CSV import — plan to start current tracking fresh and keep the Nara
archive for historical reference.

### Glow Baby Tracker
Strong growth-chart and multi-child support, free with optional premium.
No confirmed bulk CSV import — same approach as Huckleberry: start fresh,
keep the archive.

## 4. What this tool does *not* recover

- **Photos/attachments** logged in Nara. CSV export can't contain binary
  files; back these up separately (camera roll, cloud backup) before you
  lose access.
- **Any data type not yet in `schema/FIELD_MAPPING.md`'s confirmed list**
  — it's preserved raw in JSON (`raw_fields`) but not cleanly typed. If
  you have one of these categories, please contribute a sample (see
  `schema/FIELD_MAPPING.md`).
