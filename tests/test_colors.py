import math
from types import SimpleNamespace

import pytest

from app.color_utils import hex_to_rgb, rank_closest, rgb_distance, rgb_to_hex, validate_rgb


@pytest.mark.parametrize("value", [0, 255, "0", "255"])
def test_rgb_boundaries(value):
    assert validate_rgb(value, value, value) == (int(value),) * 3


@pytest.mark.parametrize("value", [-1, 256, "1.5", "", True, 1.0, "red"])
def test_invalid_rgb(value):
    with pytest.raises(ValueError):
        validate_rgb(value, 0, 0)


@pytest.mark.parametrize("value", ["#FF8000", "ff8000"])
def test_hex_conversion(value):
    assert hex_to_rgb(value) == (255, 128, 0)
    assert rgb_to_hex((255, 128, 0)) == "#FF8000"


@pytest.mark.parametrize("value", ["#FFF", "1234567", "GGGGGG", "##FFFFFF", ""])
def test_invalid_hex(value):
    with pytest.raises(ValueError):
        hex_to_rgb(value)


def test_distance_and_ranking():
    assert rgb_distance((0, 0, 0), (3, 4, 0)) == 5
    assert rgb_distance((0, 0, 0), (255, 255, 255)) == math.sqrt(3 * 255 ** 2)
    paints = [SimpleNamespace(id=2, rgb=(0, 4, 0)), SimpleNamespace(id=1, rgb=(4, 0, 0)), SimpleNamespace(id=3, rgb=(9, 0, 0))]
    assert [paint.id for paint, _ in rank_closest((0, 0, 0), paints, 100)] == [1, 2, 3]


@pytest.mark.parametrize("count", [0, -1, 1.5, True])
def test_bad_closest_count(count):
    with pytest.raises(ValueError):
        rank_closest((0, 0, 0), [], count)
