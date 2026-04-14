from typing import Optional

def calculate_max_power_for_duration(power_samples: list[Optional[int]], duration_sec: int) -> Optional[int]:
    """
    Znajduje maksymalną średnią moc dla danego czasu trwania (w sekundach).
    Zakłada 1 próbkę na sekundę.
    Ignoruje okna, w których jest za dużo None.
    """
    if duration_sec <= 0:
        return None
        
    cleaned_samples = [p if p is not None else 0 for p in power_samples]
    n = len(cleaned_samples)
    
    if n < duration_sec:
        return None

    # Obliczamy sumę początkowego okna
    current_sum = sum(cleaned_samples[:duration_sec])
    max_sum = current_sum

    for i in range(duration_sec, n):
        current_sum += cleaned_samples[i] - cleaned_samples[i - duration_sec]
        if current_sum > max_sum:
            max_sum = current_sum

    return round(max_sum / duration_sec)

def calculate_power_curve(power_samples: list[Optional[int]]) -> dict:
    """
    Oblicza punkty odniesienia dla Power Curve.
    Wymagane z dokumentacji: 5s, 1m (60s), 5m (300s), 20m (1200s).
    """
    durations = [5, 60, 300, 1200]
    result = {}
    
    for d in durations:
        result[f"sec_{d}"] = calculate_max_power_for_duration(power_samples, d)
        
    return result