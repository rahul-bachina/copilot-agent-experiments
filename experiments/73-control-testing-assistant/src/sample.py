"""Seeded systematic sample. The same seed and the same ids give the same rows.

The size rule is a starter rule. ISA (UK) 530 was not opened. A sample is
not a conclusion that a control operated.
"""

from __future__ import annotations

import math


def sample_size(population: int, minimum: object) -> dict:
    if type(minimum) is not int or minimum < 1:
        return {
            "size": None,
            "minimum": None,
            "root": None,
            "unreadable_minimum": True,
            "coerced": False,
        }
    if type(population) is not int or population < 0:
        return {
            "size": None,
            "minimum": minimum,
            "root": None,
            "unreadable_minimum": False,
            "unreadable_population": True,
            "coerced": False,
        }
    root = math.ceil(math.sqrt(population)) if population else 0
    size = min(population, max(minimum, root))
    return {
        "size": size,
        "minimum": minimum,
        "root": root,
        "unreadable_minimum": False,
        "unreadable_population": False,
        "coerced": False,
    }


def select(evidence_ids: list[str], seed: object, size: int | None) -> dict:
    ordered = sorted(evidence_id for evidence_id in evidence_ids if isinstance(evidence_id, str))
    if type(seed) is not int:
        return {
            "ids": [],
            "seed": None,
            "start": None,
            "step": None,
            "unreadable_seed": True,
            "coerced": False,
            "method": "seeded_systematic",
        }
    if size is None or type(size) is not int or size < 1 or not ordered:
        return {
            "ids": [],
            "seed": seed,
            "start": None,
            "step": None,
            "unreadable_seed": False,
            "coerced": False,
            "method": "seeded_systematic",
        }
    count = len(ordered)
    take = min(size, count)
    start = seed % count
    step = max(1, count // take)
    picked: list[str] = []
    seen: set[str] = set()
    index = start
    while len(picked) < take and len(seen) < count:
        item = ordered[index % count]
        if item not in seen:
            picked.append(item)
            seen.add(item)
        index += step
    return {
        "ids": picked,
        "seed": seed,
        "start": start,
        "step": step,
        "unreadable_seed": False,
        "coerced": False,
        "method": "seeded_systematic",
    }


def rationale(population: int, reading: dict, chosen: dict) -> str:
    if reading.get("unreadable_minimum") or chosen.get("unreadable_seed"):
        return (
            "The sample was not drawn. The minimum or the seed could not be read. "
            "It was not replaced with zero. This is a starter rule. ISA (UK) 530 was not opened."
        )
    return (
        f"The population has {population} evidence items for this control, ordered by evidence_id. "
        f"The sample size is the larger of the pinned minimum ({reading.get('minimum')}) and the "
        f"integer square root of the population rounded up ({reading.get('root')}), and it is not "
        f"larger than the population. The size is {reading.get('size')}. The method is seeded "
        f"systematic sampling. The start index is the seed modulo the population "
        f"({chosen.get('start')}). The step is the population divided by the size, using integer "
        f"division ({chosen.get('step')}). The same seed and the same evidence ids produce the "
        "same sample. This is a starter rule. ISA (UK) 530 was not opened. The sample is not a "
        "conclusion that the control operated."
    )
