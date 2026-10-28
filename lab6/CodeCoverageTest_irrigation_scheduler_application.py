"""Statement coverage test suite for irrigation_scheduler module.

Achieves >= 90% statement coverage across all functions and lines.
"""

import os
import sys

# Ensure current directory is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from irrigation_scheduler import should_irrigate, water_volume, schedule


# --- Tests for should_irrigate ---

def test_should_irrigate_high_moisture():
    """Moisture >= 60 should not irrigate."""
    assert should_irrigate(60, 0, "seedling") is False
    assert should_irrigate(75, 2, "flowering") is False


def test_should_irrigate_heavy_rain():
    """Rain >= 10mm should not irrigate."""
    assert should_irrigate(40, 10, "seedling") is False
    assert should_irrigate(30, 15, "vegetative") is False


def test_should_irrigate_seedling_dry():
    """Seedling stage with moisture < 45 should irrigate."""
    assert should_irrigate(40, 0, "seedling") is True


def test_should_irrigate_seedling_sufficient_moisture():
    """Seedling stage with moisture >= 45 should not irrigate."""
    assert should_irrigate(50, 0, "seedling") is False


def test_should_irrigate_flowering_dry():
    """Flowering stage with moisture < 55 should irrigate."""
    assert should_irrigate(50, 2, "flowering") is True


def test_should_irrigate_flowering_sufficient_moisture():
    """Flowering stage with moisture >= 55 should not irrigate."""
    assert should_irrigate(55, 2, "flowering") is False


def test_should_irrigate_other_stage_moderate_rain():
    """Default stage with rain >= 5mm should not irrigate."""
    assert should_irrigate(30, 5, "vegetative") is False


def test_should_irrigate_other_stage_dry():
    """Default stage with rain < 5mm and moisture < 40 should irrigate."""
    assert should_irrigate(35, 2, "vegetative") is True


def test_should_irrigate_other_stage_sufficient_moisture():
    """Default stage with rain < 5mm and moisture >= 40 should not irrigate."""
    assert should_irrigate(45, 2, "vegetative") is False


# --- Tests for water_volume ---

def test_water_volume_invalid_area_zero():
    """Area <= 0 should raise ValueError."""
    with pytest.raises(ValueError, match="invalid area"):
        water_volume(0, "seedling", 25)


def test_water_volume_invalid_area_negative():
    """Negative area should raise ValueError."""
    with pytest.raises(ValueError, match="invalid area"):
        water_volume(-10, "flowering", 25)


def test_water_volume_seedling_normal_temp():
    """Seedling stage with normal temperature (10 <= temp <= 35)."""
    # litres = 2; area = 10 -> 20.0
    assert water_volume(10, "seedling", 25) == 20.0


def test_water_volume_flowering_normal_temp():
    """Flowering stage with normal temperature (10 <= temp <= 35)."""
    # litres = 5; area = 10 -> 50.0
    assert water_volume(10, "flowering", 20) == 50.0


def test_water_volume_other_stage_normal_temp():
    """Other stage with normal temperature (10 <= temp <= 35)."""
    # litres = 4; area = 10 -> 40.0
    assert water_volume(10, "vegetative", 20) == 40.0


def test_water_volume_high_temperature_adjustment():
    """Temperature > 35C increases volume by 1.5x."""
    # seedling: 2 * 1.5 = 3.0; area = 10 -> 30.0
    assert water_volume(10, "seedling", 40) == 30.0


def test_water_volume_low_temperature_adjustment():
    """Temperature < 10C decreases volume by 0.5x."""
    # seedling: 2 * 0.5 = 1.0; area = 10 -> 10.0
    assert water_volume(10, "seedling", 5) == 10.0


# --- Tests for schedule ---

def test_schedule_empty_zones():
    """Empty zones list returns empty plan."""
    assert schedule([], 100) == []


def test_schedule_all_zones_satisfied():
    """All zones needing water scheduled within budget."""
    zones = [
        ("Zone_A", 10, 30, 0, "seedling", 20),   # needs 10 * 2 = 20
        ("Zone_B", 10, 40, 0, "flowering", 20),  # needs 10 * 5 = 50
    ]
    # Total need = 70, budget = 100 -> both included
    plan = schedule(zones, 100)
    assert plan == ["Zone_A", "Zone_B"]


def test_schedule_skips_unneeded_zone():
    """Zones that should not be irrigated are skipped."""
    zones = [
        ("Zone_Wet", 10, 80, 0, "seedling", 20),     # should_irrigate is False
        ("Zone_Dry", 10, 30, 0, "seedling", 20),     # should_irrigate is True, need 20
    ]
    plan = schedule(zones, 50)
    assert plan == ["Zone_Dry"]


def test_schedule_stops_when_budget_exceeded():
    """Loop breaks when zone demand exceeds remaining budget."""
    zones = [
        ("Zone_1", 10, 30, 0, "seedling", 20),   # needs 20, budget remaining: 30
        ("Zone_2", 20, 30, 0, "flowering", 20),  # needs 100 > 30 -> breaks
        ("Zone_3", 5, 30, 0, "seedling", 20),    # skipped due to break
    ]
    plan = schedule(zones, 50)
    assert plan == ["Zone_1"]
