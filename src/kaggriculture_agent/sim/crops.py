"""Crop catalog used by the mock sim and the strategy.

Values are illustrative and balanced so that different weather/market conditions
favor different crops (i.e., there is no single dominant choice).
"""

from __future__ import annotations

from ..types import Crop

CROPS: dict[str, Crop] = {
    "wheat": Crop(
        name="wheat",
        seed_cost=10.0,
        days_to_mature=4,
        base_yield=12.0,
        water_need=2,
        drought_penalty=0.15,
    ),
    "corn": Crop(
        name="corn",
        seed_cost=20.0,
        days_to_mature=6,
        base_yield=28.0,
        water_need=3,
        drought_penalty=0.25,
    ),
    "tomato": Crop(
        name="tomato",
        seed_cost=35.0,
        days_to_mature=5,
        base_yield=40.0,
        water_need=4,
        drought_penalty=0.35,
    ),
    "potato": Crop(
        name="potato",
        seed_cost=15.0,
        days_to_mature=5,
        base_yield=22.0,
        water_need=2,
        drought_penalty=0.10,
    ),
}

CROP_NAMES: list[str] = list(CROPS.keys())
