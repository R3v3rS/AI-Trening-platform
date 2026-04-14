from typing import Optional


def calculate_ftp_from_ramp_test(
    power_samples: list[Optional[int]],
    sample_rate_sec: int = 1,
) -> int:
    """
    Ramp test: FTP = średnia moc z ostatnich 60 sekund * 0.75
    Zakłada próbkowanie co sample_rate_sec sekund.
    """
    cleaned = [p for p in power_samples if p is not None]

    samples_per_minute = 60 // sample_rate_sec
    if len(cleaned) < samples_per_minute:
        raise ValueError(
            f"Za mało próbek: {len(cleaned)}. "
            f"Wymagane minimum {samples_per_minute} "
            f"(ostatnia minuta przy próbkowaniu {sample_rate_sec}s)."
        )

    last_minute = cleaned[-samples_per_minute:]
    avg_power = sum(last_minute) / len(last_minute)
    return round(avg_power * 0.75)


def calculate_ftp_from_20min_test(avg_power_20min: float) -> int:
    """
    Test 20-minutowy: FTP = średnia moc 20 minut * 0.95
    """
    if avg_power_20min <= 0:
        raise ValueError("Średnia moc musi być większa niż 0.")
    return round(avg_power_20min * 0.95)
