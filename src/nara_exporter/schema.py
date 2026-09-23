"""Normalized, app-agnostic event schema for Nara Baby export data.

This module defines the target shape that every Nara CSV row is converted
into, independent of which baby-tracking app the data eventually lands in.

The schema is intentionally *wide and flat* per event (one row = one
logged activity), with a `type` discriminator and a common envelope of
fields (who/when/where), plus type-specific fields grouped by prefix.
This mirrors Nara's own export shape but with cleaner, consistent names
and normalized units (volumes in mL, weight in kg, length in cm).

Nara's own CSV lists 7 confirmed activity types as of 2026-09-23, based on
a real, user-provided export: Breastfeed, Sleep, Diaper, Bottle Feed,
Pump, Growth, Profile. Nara's app also supports other activity/tracking
types (solids, medications, vaccines, milestones, routines, pregnancy &
postpartum tracking, journal notes/photos) that did not appear in the
sample because the sample was from a newborn's first ~3 months. Those
types are NOT yet confirmed in CSV form -- see schema/FIELD_MAPPING.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


# Activity types confirmed present in a real Nara CSV export (2026-09-23).
KNOWN_TYPES = {
    "Breastfeed": "breastfeeding",
    "Sleep": "sleep",
    "Diaper": "diaper",
    "Bottle Feed": "bottle_feeding",
    "Pump": "pumping",
    "Growth": "growth",
    "Profile": "profile",
}

# mL is the normalized volume unit; add more source units here as they're
# confirmed (Nara's own unit strings are used as keys).
_VOLUME_TO_ML = {
    "ML": 1.0,
    "OZ": 29.5735,
}

# kg is the normalized weight unit.
_WEIGHT_TO_KG = {
    "KG": 1.0,
    "LB": 0.453592,
    "G": 0.001,
}

# cm is the normalized length unit.
_LENGTH_TO_CM = {
    "CM": 1.0,
    "IN": 2.54,
}


def volume_to_ml(value: Optional[str], unit: Optional[str]) -> Optional[float]:
    """Convert a Nara volume field to milliliters, or None if not convertible."""
    return _convert(value, unit, _VOLUME_TO_ML)


def weight_to_kg(value: Optional[str], unit: Optional[str]) -> Optional[float]:
    """Convert a Nara weight field to kilograms, or None if not convertible."""
    return _convert(value, unit, _WEIGHT_TO_KG)


def length_to_cm(value: Optional[str], unit: Optional[str]) -> Optional[float]:
    """Convert a Nara length field to centimeters, or None if not convertible."""
    return _convert(value, unit, _LENGTH_TO_CM)


def _convert(value: Optional[str], unit: Optional[str], table: dict) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        numeric = float(value)
    except ValueError:
        return None
    factor = table.get((unit or "").strip().upper())
    if factor is None:
        # Unknown unit: return the raw number unconverted rather than
        # dropping it, and let callers see the original unit separately.
        return numeric
    return round(numeric * factor, 4)


@dataclass
class NormalizedEvent:
    """One normalized, app-agnostic tracked event."""

    # --- common envelope, present on (almost) every event ---
    event_id: str
    event_type: str  # e.g. "sleep", "diaper", "breastfeeding", "unknown"
    raw_type: str  # original Nara "Type" column value, for traceability
    child_name: Optional[str] = None
    child_id: Optional[str] = None
    family_id: Optional[str] = None
    start_time: Optional[str] = None  # ISO 8601, local (no tz conversion applied)
    end_time: Optional[str] = None  # ISO 8601, local
    duration_seconds: Optional[float] = None
    timezone: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    note: Optional[str] = None

    # --- breastfeeding ---
    breastfeed_begin_side: Optional[str] = None
    breastfeed_end_side: Optional[str] = None
    breastfeed_left_seconds: Optional[float] = None
    breastfeed_right_seconds: Optional[float] = None

    # --- diaper ---
    diaper_type: Optional[str] = None
    diaper_detail: Optional[str] = None
    diaper_dirty_color: Optional[str] = None
    diaper_dirty_texture: Optional[str] = None

    # --- bottle feeding ---
    bottle_type: Optional[str] = None  # e.g. "Breast Milk", "Formula"
    bottle_formula_name: Optional[str] = None
    bottle_volume_ml: Optional[float] = None

    # --- pumping ---
    pump_left_ml: Optional[float] = None
    pump_right_ml: Optional[float] = None
    pump_total_ml: Optional[float] = None

    # --- growth ---
    growth_weight_kg: Optional[float] = None
    growth_height_cm: Optional[float] = None
    growth_head_cm: Optional[float] = None

    # --- profile (one row per child, static info) ---
    profile_birth_date: Optional[str] = None
    profile_birth_date_adjusted: Optional[str] = None
    profile_sex: Optional[str] = None
    profile_type: Optional[str] = None

    # --- catch-all for unknown/not-yet-mapped activity types ---
    raw_fields: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        # Drop empty raw_fields for cleaner JSON when not needed.
        if not d.get("raw_fields"):
            d.pop("raw_fields", None)
        return d


# Column order used when writing the flat, normalized CSV output.
CSV_COLUMNS = [
    "event_id",
    "event_type",
    "raw_type",
    "child_name",
    "child_id",
    "family_id",
    "start_time",
    "end_time",
    "duration_seconds",
    "timezone",
    "created_by",
    "updated_by",
    "note",
    "breastfeed_begin_side",
    "breastfeed_end_side",
    "breastfeed_left_seconds",
    "breastfeed_right_seconds",
    "diaper_type",
    "diaper_detail",
    "diaper_dirty_color",
    "diaper_dirty_texture",
    "bottle_type",
    "bottle_formula_name",
    "bottle_volume_ml",
    "pump_left_ml",
    "pump_right_ml",
    "pump_total_ml",
    "growth_weight_kg",
    "growth_height_cm",
    "growth_head_cm",
    "profile_birth_date",
    "profile_birth_date_adjusted",
    "profile_sex",
    "profile_type",
]
