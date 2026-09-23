"""Convert raw Nara CSV rows into `NormalizedEvent` objects."""

from __future__ import annotations

from typing import Iterable, Iterator

from .schema import KNOWN_TYPES, NormalizedEvent, volume_to_ml, weight_to_kg, length_to_cm

# Columns that belong to the common envelope, i.e. never type-specific.
_ENVELOPE_COLUMNS = {
    "Type",
    "Profile Name",
    "Start Date/time",
    "Start Date/time (Epoch)",
    "Created By Caregiver",
    "Last Updated By Caregiver",
    "Note",
    "Time Zone",
    "_familyKey",
    "_profileKey",
    "_activityKey",
}


def normalize_row(row: dict, index: int) -> NormalizedEvent:
    """Convert one raw Nara CSV row (as a dict) into a NormalizedEvent."""
    raw_type = (row.get("Type") or "").strip()
    event_type = KNOWN_TYPES.get(raw_type, "unknown")

    event_id = row.get("_activityKey") or f"row-{index}"

    event = NormalizedEvent(
        event_id=event_id,
        event_type=event_type,
        raw_type=raw_type or "(missing)",
        child_name=row.get("Profile Name") or None,
        child_id=row.get("_profileKey") or None,
        family_id=row.get("_familyKey") or None,
        start_time=row.get("Start Date/time") or None,
        timezone=row.get("Time Zone") or None,
        created_by=row.get("Created By Caregiver") or None,
        updated_by=row.get("Last Updated By Caregiver") or None,
        note=row.get("Note") or None,
    )

    if raw_type == "Breastfeed":
        _apply_breastfeed(event, row)
    elif raw_type == "Sleep":
        _apply_sleep(event, row)
    elif raw_type == "Diaper":
        _apply_diaper(event, row)
    elif raw_type == "Bottle Feed":
        _apply_bottle_feed(event, row)
    elif raw_type == "Pump":
        _apply_pump(event, row)
    elif raw_type == "Growth":
        _apply_growth(event, row)
    elif raw_type == "Profile":
        _apply_profile(event, row)
    else:
        # Unknown/not-yet-mapped activity type: preserve every non-empty,
        # non-envelope column so no data is silently lost.
        event.raw_fields = {
            key: value
            for key, value in row.items()
            if key not in _ENVELOPE_COLUMNS and (value or "").strip()
        }

    return event


def _num(row: dict, key: str) -> float | None:
    value = row.get(key)
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _apply_breastfeed(event: NormalizedEvent, row: dict) -> None:
    event.breastfeed_begin_side = row.get("[Breastfeed] Begin Side") or None
    event.breastfeed_end_side = row.get("[Breastfeed] End Side") or None
    event.breastfeed_left_seconds = _num(row, "[Breastfeed] Left Duration (Seconds)")
    event.breastfeed_right_seconds = _num(row, "[Breastfeed] Right Duration (Seconds)")
    parts = [
        s for s in (event.breastfeed_left_seconds, event.breastfeed_right_seconds) if s is not None
    ]
    if parts:
        event.duration_seconds = sum(parts)


def _apply_sleep(event: NormalizedEvent, row: dict) -> None:
    event.duration_seconds = _num(row, "[Sleep] Duration (Seconds)")
    event.end_time = row.get("[Sleep] End Date/time") or None


def _apply_diaper(event: NormalizedEvent, row: dict) -> None:
    event.diaper_type = row.get("[Diaper] Type") or None
    event.diaper_detail = row.get("[Diaper] Detail") or None
    event.diaper_dirty_color = row.get("[Diaper] Dirty Color") or None
    event.diaper_dirty_texture = row.get("[Diaper] Dirty Texture") or None


def _apply_bottle_feed(event: NormalizedEvent, row: dict) -> None:
    event.bottle_type = row.get("[Bottle Feed] Type") or None
    event.bottle_formula_name = row.get("[Bottle Feed] Formula Name") or None

    # Nara splits bottle volume across up to three possible column sets
    # depending on content (breast milk / formula / generic "Volume").
    # Take whichever is populated; normalize all to mL.
    candidates = [
        (row.get("[Bottle Feed] Breast Milk Volume"), row.get("[Bottle Feed] Breast Milk Volume Unit")),
        (row.get("[Bottle Feed] Formula Volume"), row.get("[Bottle Feed] Formula Volume Unit")),
        (row.get("[Bottle Feed] Volume"), row.get("[Bottle Feed] Volume Unit")),
    ]
    for value, unit in candidates:
        if value:
            event.bottle_volume_ml = volume_to_ml(value, unit)
            break


def _apply_pump(event: NormalizedEvent, row: dict) -> None:
    event.duration_seconds = _num(row, "[Pump] Duration (Seconds)")
    event.end_time = row.get("[Pump] End Date/time") or None
    event.pump_left_ml = volume_to_ml(row.get("[Pump] Left Volume"), row.get("[Pump] Left Volume Unit"))
    event.pump_right_ml = volume_to_ml(row.get("[Pump] Right Volume"), row.get("[Pump] Right Volume Unit"))
    event.pump_total_ml = volume_to_ml(row.get("[Pump] Total Volume"), row.get("[Pump] Total Volume Unit"))


def _apply_growth(event: NormalizedEvent, row: dict) -> None:
    event.growth_weight_kg = weight_to_kg(row.get("[Growth] Weight"), row.get("[Growth] Weight Unit"))
    event.growth_height_cm = length_to_cm(row.get("[Growth] Height"), row.get("[Growth] Height Unit"))
    event.growth_head_cm = length_to_cm(row.get("[Growth] Head Size"), row.get("[Growth] Head Size Unit"))


def _apply_profile(event: NormalizedEvent, row: dict) -> None:
    event.profile_birth_date = row.get("[Profile] Birth Date") or None
    event.profile_birth_date_adjusted = row.get("[Profile] Birth Date (Adjusted)") or None
    event.profile_sex = row.get("[Profile] Sex") or None
    event.profile_type = row.get("[Profile] Type") or None


def normalize_rows(rows: Iterable[dict]) -> Iterator[NormalizedEvent]:
    for index, row in enumerate(rows):
        yield normalize_row(row, index)
