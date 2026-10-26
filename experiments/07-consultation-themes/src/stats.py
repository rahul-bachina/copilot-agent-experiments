"""Wilson score interval for a proportion.

This is the sampling uncertainty of a count divided by a denominator. It is
not a model confidence score, and it does not include coding error.
"""

from __future__ import annotations

import math

Z_95 = 1.96


def wilson_interval(successes: int, total: int, z: float = Z_95) -> tuple[float, float]:
    """Return the lower and upper bounds of a Wilson interval.

    Bounds are clipped to [0, 1]. A zero denominator returns (0.0, 0.0).
    """
    if total < 0 or successes < 0 or successes > total:
        raise ValueError("successes must be between 0 and total")
    if total == 0:
        return (0.0, 0.0)
    proportion = successes / total
    z2 = z * z
    denominator = 1 + z2 / total
    centre = (proportion + z2 / (2 * total)) / denominator
    margin = z * math.sqrt((proportion * (1 - proportion) + z2 / (4 * total)) / total) / denominator
    low = max(0.0, centre - margin)
    high = min(1.0, centre + margin)
    return (low, high)


def round6(value: float) -> float:
    return round(value, 6)
