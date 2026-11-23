import pytest
from etl.district_zones import (
    CANONICAL_NABARD_NAMES,
    NABARD_DISTRICT_BASE_MAP,
    resolve_district_classification,
)

EXPECTED_NABARD_TABLE = {
    # AZ10 - Undulating Plain (3)
    "S.A.S Nagar": ("AZ10", "Undulating Plain"),
    "Shahid Bhagat Singh Nagar": ("AZ10", "Undulating Plain"),
    "Rupnagar": ("AZ10", "Undulating Plain"),
    # AZ11 - Central Plain (10)
    "Amritsar": ("AZ11", "Central Plain"),
    "Tarn Taran": ("AZ11", "Central Plain"),
    "Kapurthala": ("AZ11", "Central Plain"),
    "Jalandhar": ("AZ11", "Central Plain"),
    "Ludhiana": ("AZ11", "Central Plain"),
    "Patiala": ("AZ11", "Central Plain"),
    "Barnala": ("AZ11", "Central Plain"),
    "Sangrur": ("AZ11", "Central Plain"),
    "Malerkotla": ("AZ11", "Central Plain"),
    "Fatehgarh Sahib": ("AZ11", "Central Plain"),
    # AZ12 - Western Plain (2)
    "Faridkot": ("AZ12", "Western Plain"),
    "Ferozepur": ("AZ12", "Western Plain"),
    # AZ13 - Western (5)
    "Bathinda": ("AZ13", "Western"),
    "Fazilka": ("AZ13", "Western"),
    "Mansa": ("AZ13", "Western"),
    "Moga": ("AZ13", "Western"),
    "Sri Muktsar Sahib": ("AZ13", "Western"),
    # AZ14 - Sub Montane Undulating (3)
    "Gurdaspur": ("AZ14", "Sub Montane Undulating"),
    "Pathankot": ("AZ14", "Sub Montane Undulating"),
    "Hoshiarpur": ("AZ14", "Sub Montane Undulating"),
}


def test_total_district_count_is_23():
    assert len(EXPECTED_NABARD_TABLE) == 23
    assert len(NABARD_DISTRICT_BASE_MAP) == 23
    assert len(CANONICAL_NABARD_NAMES) == 23


@pytest.mark.parametrize("district_label,expected", EXPECTED_NABARD_TABLE.items())
def test_all_23_canonical_nabard_districts(district_label, expected):
    az_code, az_name = expected
    result = resolve_district_classification(district_label)
    assert result["district_nabard"] == district_label
    assert result["nabard_az_code"] == az_code
    assert result["nabard_az_name"] == az_name
    assert result["nabard_source_version"] == "2025-26.1"
    assert result["pau_physiographic_zone_id"] is None
    assert result["pau_physiographic_zone_name"] is None


@pytest.mark.parametrize(
    "messy_input,expected_canonical,expected_az",
    [
        ("  mohali  ", "S.A.S Nagar", "AZ10"),
        ("SAS Nagar (Mohali)", "S.A.S Nagar", "AZ10"),
        ("s.a.s. nagar", "S.A.S Nagar", "AZ10"),
        ("NAWANSHAHR", "Shahid Bhagat Singh Nagar", "AZ10"),
        ("Shaheed Bhagat Singh Nagar", "Shahid Bhagat Singh Nagar", "AZ10"),
        ("SBS Nagar", "Shahid Bhagat Singh Nagar", "AZ10"),
        ("  Ropar ", "Rupnagar", "AZ10"),
        ("FIROZPUR", "Ferozepur", "AZ12"),
        ("Muktsar", "Sri Muktsar Sahib", "AZ13"),
        ("Bhatinda", "Bathinda", "AZ13"),
        ("Jullundur", "Jalandhar", "AZ11"),
        ("Tarntaran", "Tarn Taran", "AZ11"),
    ],
)
def test_aliases_and_normalization(messy_input, expected_canonical, expected_az):
    result = resolve_district_classification(messy_input)
    assert result["district_nabard"] == expected_canonical
    assert result["nabard_az_code"] == expected_az


@pytest.mark.parametrize("invalid_input", ["", "   ", "Karnal", "Ambala", "Unknown District", "12345"])
def test_unknown_districts_raise_value_error(invalid_input):
    with pytest.raises(ValueError, match="Unrecognized Punjab district"):
        resolve_district_classification(invalid_input)


def test_unverified_floodplain_override_is_rejected():
    with pytest.raises(ValueError, match="requires verified=True"):
        resolve_district_classification(
            "Ludhiana",
            pau_spatial_overlay={"pau_zone_id": 6, "granularity": "village_boundary"},
        )

    with pytest.raises(ValueError, match="requires verified=True"):
        resolve_district_classification(
            "Ludhiana",
            pau_spatial_overlay={
                "pau_zone_id": 6,
                "verified": True,
                "granularity": "district",
            },
        )


def test_verified_floodplain_overlay_preserves_nabard_base():
    verified_bet = {
        "pau_zone_id": 6,
        "verified": True,
        "granularity": "village_boundary",
        "river_basin": "Sutlej",
        "overlay_source": "PRSC / PAU Physiographic Layer",
    }
    result = resolve_district_classification("Ludhiana", pau_spatial_overlay=verified_bet)
    assert result["district_nabard"] == "Ludhiana"
    assert result["nabard_az_code"] == "AZ11"
    assert result["nabard_az_name"] == "Central Plain"
    assert result["pau_physiographic_zone_id"] == 6
    assert result["pau_physiographic_zone_name"] == "Flood Plain"
    assert result["pau_overlay_granularity"] == "village_boundary"
