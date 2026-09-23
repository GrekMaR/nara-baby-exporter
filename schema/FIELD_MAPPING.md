# Field Mapping Matrix

This maps Nara Baby's official CSV export columns to the normalized schema
produced by this tool (`src/nara_exporter/schema.py`). Confidence levels:

- **Confirmed**: verified against a real, user-provided Nara export
  (2026-09-23, ~3 months of data, 692 rows).
- **Provisional**: Nara's app supports this feature/data, but no row of
  this type appeared in the sample export used to build this tool, so the
  exact CSV column names are inferred from Nara's documented feature list,
  not verified. **If you have a real export containing any of these
  categories, please open an issue or PR with the raw header row (no
  personal data needed) so we can confirm and refine the mapping.**

## Common envelope (every row)

| Nara column | Normalized field | Notes |
|---|---|---|
| `Type` | `raw_type` / `event_type` | `event_type` is the normalized lowercase name (see table below); `raw_type` keeps Nara's original string. |
| `Profile Name` | `child_name` | |
| `Start Date/time` | `start_time` | Local time, no timezone conversion applied. |
| `Start Date/time (Epoch)` | *(not carried over)* | Redundant with `start_time`; epoch ms if you need it, re-derive from the raw CSV. |
| `Created By Caregiver` | `created_by` | |
| `Last Updated By Caregiver` | `updated_by` | |
| `Note` | `note` | Free text. |
| `Time Zone` | `timezone` | IANA name, e.g. `Europe/Copenhagen`. |
| `_familyKey` | `family_id` | |
| `_profileKey` | `child_id` | |
| `_activityKey` | `event_id` | Falls back to a synthetic `row-N` id if blank (seen on `Profile` rows). |

**Confidence: Confirmed** (all of the above).

## Per-type fields

| Nara `Type` | Normalized `event_type` | Nara columns | Normalized fields | Confidence |
|---|---|---|---|---|
| `Breastfeed` | `breastfeeding` | `[Breastfeed] Begin Side`, `End Side`, `Left Duration (Seconds)`, `Right Duration (Seconds)` | `breastfeed_begin_side`, `breastfeed_end_side`, `breastfeed_left_seconds`, `breastfeed_right_seconds`, `duration_seconds` (= left + right) | Confirmed |
| `Sleep` | `sleep` | `[Sleep] Duration (Seconds)`, `End Date/time`, `End Date/time (Epoch)` | `duration_seconds`, `end_time` | Confirmed |
| `Diaper` | `diaper` | `[Diaper] Type`, `Detail`, `Dirty Color`, `Dirty Texture` | `diaper_type`, `diaper_detail`, `diaper_dirty_color`, `diaper_dirty_texture` | Confirmed |
| `Bottle Feed` | `bottle_feeding` | `[Bottle Feed] Type`, `Breast Milk Volume(+Unit)`, `Formula Name`, `Formula Volume(+Unit)`, `Volume(+Unit)` | `bottle_type`, `bottle_formula_name`, `bottle_volume_ml` (normalized from whichever volume column is populated) | Confirmed |
| `Pump` | `pumping` | `[Pump] Duration (Seconds)`, `End Date/time(+Epoch)`, `Left/Right/Total Volume(+Unit)` | `duration_seconds`, `end_time`, `pump_left_ml`, `pump_right_ml`, `pump_total_ml` | Confirmed |
| `Growth` | `growth` | `[Growth] Head Size(+Unit)`, `Height(+Unit)`, `Weight(+Unit)` | `growth_head_cm`, `growth_height_cm`, `growth_weight_kg` | Confirmed |
| `Profile` | `profile` | `[Profile] Birth Date`, `Birth Date (Adjusted)`, `Sex`, `Type` | `profile_birth_date`, `profile_birth_date_adjusted`, `profile_sex`, `profile_type` | Confirmed |
| *(various)* | `unknown` | any columns not in the envelope | preserved verbatim in `raw_fields` (JSON output only) | N/A — fallback |

## Not yet confirmed in CSV form

Nara's app (per its own marketing/FAQ pages) also supports these, but none
appeared in the sample export, likely because it came from a newborn's
first ~3 months:

- **Solids/first foods**
- **Medications**
- **Vaccines**
- **Developmental milestones**
- **Routines** (tummy time, baths, story time, etc.)
- **Pregnancy & postpartum tracking** (vitals, mood, journal entries)
- **Photos/attachments** attached to any entry

If your export contains any of these, the parser will **not** crash or
drop the row — it will classify it as `event_type: "unknown"` and put every
non-empty column into `raw_fields` in the JSON output (CSV output only
gets the common envelope columns, since `raw_fields` doesn't have a fixed
shape). Run `nara-export summary your_export.csv` to see a warning listing
any unmapped types found, then please contribute a sample so we can add
proper columns.

**Known gap:** photos/attachments are very unlikely to be included in any
CSV export at all (CSV can't embed binary files). If you need to preserve
photos, back them up separately (e.g. from your phone's camera roll,
Nara's cloud backups, or your target app's own photo-import feature)
before your account goes read-only or you cancel.
