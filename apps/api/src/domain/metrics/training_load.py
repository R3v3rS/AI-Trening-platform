from __future__ import annotations

from math import pow
from typing import Optional


class MetricsError(Exception):
    pass


def calculate_np(power_samples: list[Optional[float]], window_size: int = 30) -> Optional[float]:
    values = [float(v) for v in power_samples if v is not None]
    if not values:
        return None

    if len(values) < window_size:
        return round(_avg(values), 2)

    rolling = []
    current_sum = sum(values[:window_size])
    rolling.append(current_sum / window_size)

    for idx in range(window_size, len(values)):
        current_sum += values[idx] - values[idx - window_size]
        rolling.append(current_sum / window_size)

    fourth_power_mean = _avg([pow(v, 4) for v in rolling])
    return round(pow(fourth_power_mean, 0.25), 2)


def calculate_if(np_value: Optional[float], ftp: Optional[float]) -> Optional[float]:
    if np_value is None or ftp is None:
        return None
    if ftp <= 0:
        raise MetricsError("FTP must be greater than 0")
    return round(np_value / ftp, 3)


def calculate_tss(
    duration_sec: Optional[float],
    np_value: Optional[float],
    if_value: Optional[float],
    ftp: Optional[float],
) -> Optional[float]:
    if None in (duration_sec, np_value, if_value, ftp):
        return None
    if duration_sec <= 0:
        raise MetricsError("Duration must be greater than 0")
    if ftp <= 0:
        raise MetricsError("FTP must be greater than 0")

    tss = (float(duration_sec) * float(np_value) * float(if_value)) / (float(ftp) * 3600.0) * 100.0
    return round(tss, 2)


def calculate_metrics(
    power_samples: list[Optional[float]],
    duration_sec: Optional[float],
    ftp: Optional[float],
) -> dict:
    np_value = calculate_np(power_samples)
    if_value = calculate_if(np_value, ftp)
    tss = calculate_tss(duration_sec, np_value, if_value, ftp)
    return {
        "np": np_value,
        "if": if_value,
        "tss": tss,
    }


def _avg(values: list[float]) -> float:
    return sum(values) / len(values)
