import re
from typing import Optional

CLASSIFICATION_METADATA = {
    "nabard_taxonomy": {
        "schema_name": "nabard_punjab_agro_climatic_zones",
        "version": "2025-26.1",
        "source": "NABARD Punjab State Focus Paper 2025-26, printed page 34 (PDF page 35)",
        "granularity": "district",
        "district_count": 23,
    },
    "pau_physiographic_taxonomy": {
        "schema_name": "pau_six_zone_physiographic_classification",
        "version": "1.0.0",
        "source": "Punjab Agricultural University (PAU), Ludhiana / PRSC Spatial Overlay",
        "granularity": "block_or_village_polygon",
        "policy": "Kept separate from district-level NABARD AZ codes; never inferred from district name alone.",
    },
}

NABARD_AZ_DESCRIPTIONS = {
    "AZ10": "Undulating Plain",
    "AZ11": "Central Plain",
    "AZ12": "Western Plain",
    "AZ13": "Western",
    "AZ14": "Sub Montane Undulating",
}

PAU_PHYSIOGRAPHIC_ZONES = {
    1: "Sub-Mountain Undulating",
    2: "Undulating Plain",
    3: "Central Plain",
    4: "Western Plain",
    5: "Western",
    6: "Flood Plain",  # Bet belts (Ravi, Beas, Sutlej, Ghaggar)
}

# Exact 23-district transcription from NABARD Punjab State Focus Paper 2025-26 (p. 34)
NABARD_DISTRICT_BASE_MAP = {
    # AZ10 - Undulating Plain (3)
    "s a s nagar": "AZ10",
    "shahid bhagat singh nagar": "AZ10",
    "rupnagar": "AZ10",

    # AZ11 - Central Plain (10)
    "amritsar": "AZ11",
    "tarn taran": "AZ11",
    "kapurthala": "AZ11",
    "jalandhar": "AZ11",
    "ludhiana": "AZ11",
    "patiala": "AZ11",
    "barnala": "AZ11",
    "sangrur": "AZ11",
    "malerkotla": "AZ11",
    "fatehgarh sahib": "AZ11",

    # AZ12 - Western Plain (2)
    "faridkot": "AZ12",
    "ferozepur": "AZ12",

    # AZ13 - Western (5)
    "bathinda": "AZ13",
    "fazilka": "AZ13",
    "mansa": "AZ13",
    "moga": "AZ13",
    "sri muktsar sahib": "AZ13",

    # AZ14 - Sub Montane Undulating (3)
    "gurdaspur": "AZ14",
    "pathankot": "AZ14",
    "hoshiarpur": "AZ14",
}

CANONICAL_NABARD_NAMES = {
    "s a s nagar": "S.A.S Nagar",
    "shahid bhagat singh nagar": "Shahid Bhagat Singh Nagar",
    "rupnagar": "Rupnagar",
    "amritsar": "Amritsar",
    "tarn taran": "Tarn Taran",
    "kapurthala": "Kapurthala",
    "jalandhar": "Jalandhar",
    "ludhiana": "Ludhiana",
    "patiala": "Patiala",
    "barnala": "Barnala",
    "sangrur": "Sangrur",
    "malerkotla": "Malerkotla",
    "fatehgarh sahib": "Fatehgarh Sahib",
    "faridkot": "Faridkot",
    "ferozepur": "Ferozepur",
    "bathinda": "Bathinda",
    "fazilka": "Fazilka",
    "mansa": "Mansa",
    "moga": "Moga",
    "sri muktsar sahib": "Sri Muktsar Sahib",
    "gurdaspur": "Gurdaspur",
    "pathankot": "Pathankot",
    "hoshiarpur": "Hoshiarpur",
}

DISTRICT_ALIASES = {
    "mohali": "s a s nagar",
    "sas nagar": "s a s nagar",
    "sahibzada ajit singh nagar": "s a s nagar",
    "sbs nagar": "shahid bhagat singh nagar",
    "s b s nagar": "shahid bhagat singh nagar",
    "shaheed bhagat singh nagar": "shahid bhagat singh nagar",
    "nawanshahr": "shahid bhagat singh nagar",
    "nawan shahr": "shahid bhagat singh nagar",
    "ropar": "rupnagar",
    "firozpur": "ferozepur",
    "ferozpur": "ferozepur",
    "muktsar": "sri muktsar sahib",
    "mukatsar": "sri muktsar sahib",
    "sri mukatsar sahib": "sri muktsar sahib",
    "bhatinda": "bathinda",
    "jullundur": "jalandhar",
    "tarntaran": "tarn taran",
}

VALID_OVERLAY_GRANULARITIES = {"village_boundary", "block_boundary", "gps_coordinate"}


def _verify_nabard_table_integrity() -> None:
    expected_counts = {"AZ10": 3, "AZ11": 10, "AZ12": 2, "AZ13": 5, "AZ14": 3}
    actual_counts = {code: 0 for code in expected_counts}
    for code in NABARD_DISTRICT_BASE_MAP.values():
        actual_counts[code] += 1
    assert len(NABARD_DISTRICT_BASE_MAP) == 23, "Expected exactly 23 Punjab districts."
    assert actual_counts == expected_counts, f"AZ distribution mismatch: {actual_counts}"


_verify_nabard_table_integrity()


def normalize_district_key(raw_name: str) -> str:
    if not isinstance(raw_name, str) or not raw_name.strip():
        return ""
    cleaned = raw_name.lower().strip()
    cleaned = re.sub(r"\(.*?\)", "", cleaned)
    cleaned = cleaned.replace(".", " ")
    cleaned = re.sub(r"[^a-z\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return DISTRICT_ALIASES.get(cleaned, cleaned)


def resolve_district_classification(
    raw_district: str,
    pau_spatial_overlay: Optional[dict] = None,
) -> dict:
    norm_key = normalize_district_key(raw_district)
    if norm_key not in NABARD_DISTRICT_BASE_MAP:
        raise ValueError(f"Unrecognized Punjab district: '{raw_district}' (normalized: '{norm_key}')")

    az_code = NABARD_DISTRICT_BASE_MAP[norm_key]
    pau_zone_id = None
    pau_zone_name = None
    overlay_granularity = None
    overlay_source = None

    if pau_spatial_overlay is not None:
        if not isinstance(pau_spatial_overlay, dict):
            raise TypeError("pau_spatial_overlay must be a dict or None.")
        zone_id = pau_spatial_overlay.get("pau_zone_id")
        granularity = pau_spatial_overlay.get("granularity")
        if (
            pau_spatial_overlay.get("verified") is not True
            or granularity not in VALID_OVERLAY_GRANULARITIES
            or zone_id not in PAU_PHYSIOGRAPHIC_ZONES
        ):
            raise ValueError(
                "PAU physiographic zone assignment requires verified=True, valid pau_zone_id (1-6), "
                f"and granularity in {sorted(VALID_OVERLAY_GRANULARITIES)}."
            )
        pau_zone_id = zone_id
        pau_zone_name = PAU_PHYSIOGRAPHIC_ZONES[zone_id]
        overlay_granularity = granularity
        overlay_source = pau_spatial_overlay.get("overlay_source", "Verified Spatial Overlay")

    return {
        "district_nabard": CANONICAL_NABARD_NAMES[norm_key],
        "nabard_az_code": az_code,
        "nabard_az_name": NABARD_AZ_DESCRIPTIONS[az_code],
        "nabard_source_version": CLASSIFICATION_METADATA["nabard_taxonomy"]["version"],
        "pau_physiographic_zone_id": pau_zone_id,
        "pau_physiographic_zone_name": pau_zone_name,
        "pau_overlay_granularity": overlay_granularity,
        "pau_overlay_source": overlay_source,
    }
