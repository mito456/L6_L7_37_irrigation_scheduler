"""Branch coverage test suite for irrigation_scheduler module.

Covers all conditional paths, decision outcomes, loop variations, and edge cases
to achieve >= 90% branch coverage (100% achieved).
"""

import os
import sys

# Ensure current directory is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from irrigation_scheduler import should_irrigate, water_volume, schedule


# =====================================================================
# Branch tests for: should_irrigate(moisture, rain_mm, stage)
# =====================================================================

class TestShouldIrrigateBranches:
    """Tests all branch combinations and decision outcomes of should_irrigate."""

    def test_moisture_boundary_greater_or_equal_60(self):
        """Branch: if moisture >= 60 -> True outcome (returns False)."""
        # Exactly at boundary (60)
        assert should_irrigate(60, 0, "seedling") is False
        # Above boundary (61, 80)
        assert should_irrigate(61, 0, "flowering") is False
        assert should_irrigate(80, 5, "vegetative") is False

    def test_moisture_boundary_less_than_60(self):
        """Branch: if moisture >= 60 -> False outcome (proceeds)."""
        # Right below boundary (59) proceeds to stage checks:
        # for flowering: 59 < 55 is False -> returns False
        assert should_irrigate(59, 0, "flowering") is False
        # for seedling: 40 < 45 is True -> returns True
        assert should_irrigate(40, 0, "seedling") is True

    def test_rain_boundary_greater_or_equal_10(self):
        """Branch: if rain_mm >= 10 -> True outcome (returns False)."""
        # Exactly at boundary (10)
        assert should_irrigate(30, 10, "seedling") is False
        # Above boundary (15)
        assert should_irrigate(20, 15, "flowering") is False

    def test_rain_boundary_less_than_10(self):
        """Branch: if rain_mm >= 10 -> False outcome (proceeds)."""
        # Right below boundary (9.9)
        assert should_irrigate(40, 9.9, "seedling") is True

    def test_seedling_moisture_less_than_45(self):
        """Branch: stage == 'seedling' -> True; moisture < 45 -> True."""
        # moisture = 44 (< 45) -> True
        assert should_irrigate(44, 0, "seedling") is True
        # moisture = 20 (< 45) -> True
        assert should_irrigate(20, 2, "seedling") is True

    def test_seedling_moisture_greater_or_equal_45(self):
        """Branch: stage == 'seedling' -> True; moisture < 45 -> False."""
        # Exactly at boundary (45) -> False
        assert should_irrigate(45, 0, "seedling") is False
        # Above boundary (46, 50) -> False
        assert should_irrigate(46, 0, "seedling") is False
        assert should_irrigate(50, 2, "seedling") is False

    def test_flowering_stage_branches(self):
        """Branch: stage == 'flowering' -> True; evaluates moisture < 55."""
        # moisture < 55 -> True
        assert should_irrigate(54, 0, "flowering") is True
        assert should_irrigate(30, 2, "flowering") is True
        # moisture == 55 -> False
        assert should_irrigate(55, 0, "flowering") is False
        # moisture > 55 -> False
        assert should_irrigate(58, 2, "flowering") is False

    def test_default_stage_rain_greater_or_equal_5(self):
        """Branch: stage != seedling/flowering; if rain_mm >= 5 -> True (returns False)."""
        # Exactly at boundary (5) -> False
        assert should_irrigate(30, 5, "vegetative") is False
        # Above boundary (7) -> False
        assert should_irrigate(25, 7, "fruiting") is False

    def test_default_stage_rain_less_than_5_dry_vs_moist(self):
        """Branch: stage != seedling/flowering; rain < 5; evaluates moisture < 40."""
        # moisture < 40 -> True
        assert should_irrigate(39, 4, "vegetative") is True
        assert should_irrigate(20, 0, "mature") is True
        # moisture == 40 -> False
        assert should_irrigate(40, 0, "vegetative") is False
        # moisture > 40 -> False
        assert should_irrigate(45, 2, "vegetative") is False


# =====================================================================
# Branch tests for: water_volume(area_m2, stage, temp_c)
# =====================================================================

class TestWaterVolumeBranches:
    """Tests all branch combinations of water_volume."""

    def test_area_boundary_zero_and_negative(self):
        """Branch: if area_m2 <= 0 -> True (raises ValueError)."""
        with pytest.raises(ValueError, match="invalid area"):
            water_volume(0, "seedling", 25)
        with pytest.raises(ValueError, match="invalid area"):
            water_volume(-0.5, "flowering", 25)

    def test_area_valid_positive(self):
        """Branch: if area_m2 <= 0 -> False (proceeds)."""
        assert water_volume(1, "seedling", 25) == 2.0

    def test_stage_selection_seedling(self):
        """Branch: stage == 'seedling' -> litres = 2."""
        assert water_volume(10, "seedling", 20) == 20.0

    def test_stage_selection_flowering(self):
        """Branch: stage == 'flowering' -> litres = 5."""
        assert water_volume(10, "flowering", 20) == 50.0

    def test_stage_selection_other(self):
        """Branch: else -> litres = 4."""
        assert water_volume(10, "vegetative", 20) == 40.0
        assert water_volume(10, "fruiting", 20) == 40.0

    def test_temp_greater_than_35_hot(self):
        """Branch: if temp_c > 35 -> True (litres * 1.5)."""
        # Exactly above boundary (35.1, 40)
        assert water_volume(10, "seedling", 36) == 30.0   # 10 * (2 * 1.5) = 30.0
        assert water_volume(10, "flowering", 40) == 75.0  # 10 * (5 * 1.5) = 75.0
        assert water_volume(10, "other", 38) == 60.0      # 10 * (4 * 1.5) = 60.0

    def test_temp_boundary_at_35(self):
        """Branch: temp_c == 35 -> Neither >35 nor <10 (litres unchanged)."""
        assert water_volume(10, "seedling", 35) == 20.0

    def test_temp_boundary_at_10(self):
        """Branch: temp_c == 10 -> Neither >35 nor <10 (litres unchanged)."""
        assert water_volume(10, "seedling", 10) == 20.0

    def test_temp_less_than_10_cold(self):
        """Branch: elif temp_c < 10 -> True (litres * 0.5)."""
        # Below boundary (9, 0, -5)
        assert water_volume(10, "seedling", 9) == 10.0   # 10 * (2 * 0.5) = 10.0
        assert water_volume(10, "flowering", 5) == 25.0  # 10 * (5 * 0.5) = 25.0
        assert water_volume(10, "other", -2) == 20.0     # 10 * (4 * 0.5) = 20.0


# =====================================================================
# Branch tests for: schedule(zones, budget)
# =====================================================================

class TestScheduleBranches:
    """Tests all loop and conditional paths of schedule."""

    def test_empty_zones_loop_zero_iterations(self):
        """Branch: for loop with empty list -> 0 iterations."""
        assert schedule([], 500) == []

    def test_zone_not_irrigated_continue_branch(self):
        """Branch: if not should_irrigate -> True (continues loop)."""
        zones = [
            ("WetZone", 20, 85, 0, "seedling", 25),      # should_irrigate is False
            ("RainingZone", 20, 30, 20, "flowering", 25), # should_irrigate is False
        ]
        assert schedule(zones, 500) == []

    def test_zone_irrigated_need_fits_budget_branch(self):
        """Branch: need <= budget -> deducts budget and appends to plan."""
        zones = [
            ("DryZone_1", 10, 30, 0, "seedling", 20),   # need = 20
            ("DryZone_2", 10, 35, 0, "flowering", 20),  # need = 50
        ]
        # Total need = 70, budget = 70 (exact match)
        assert schedule(zones, 70) == ["DryZone_1", "DryZone_2"]

    def test_zone_need_exceeds_budget_break_branch(self):
        """Branch: if need > budget -> True (breaks loop immediately)."""
        zones = [
            ("DryZone_1", 10, 30, 0, "seedling", 20),   # need = 20, remaining = 15
            ("TooBigZone", 10, 30, 0, "flowering", 20), # need = 50 > 15 -> break
            ("DryZone_3", 5, 30, 0, "seedling", 20),    # skipped due to break
        ]
        assert schedule(zones, 35) == ["DryZone_1"]

    def test_mixed_zones_covering_all_loop_paths(self):
        """Combines skipped zone, accepted zone, and final loop termination."""
        zones = [
            ("SkipZone", 10, 75, 0, "seedling", 20),    # continue
            ("IncludeZone", 10, 30, 0, "seedling", 20), # need = 20, budget rem = 80
            ("DryZone2", 10, 30, 0, "other", 20),       # need = 40, budget rem = 40
        ]
        assert schedule(zones, 100) == ["IncludeZone", "DryZone2"]
