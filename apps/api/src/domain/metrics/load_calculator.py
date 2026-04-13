import math
from datetime import date, timedelta


def calculate_atl(
    daily_tss: dict[date, float],
    target_date: date,
    days: int = 7
) -> float:
    """
    Acute Training Load – exponential weighted average z 7 dni.
    daily_tss: słownik {date: tss_value}
    """
    decay = math.exp(-1 / days)
    atl = 0.0
    for i in range(days * 3):
        d = target_date - timedelta(days=i)
        tss = daily_tss.get(d, 0.0)
        weight = (1 - decay) * (decay ** i)
        atl += tss * weight
    return round(atl, 2)


def calculate_ctl(
    daily_tss: dict[date, float],
    target_date: date,
    days: int = 42
) -> float:
    """
    Chronic Training Load – exponential weighted average z 42 dni.
    """
    decay = math.exp(-1 / days)
    ctl = 0.0
    for i in range(days * 3):
        d = target_date - timedelta(days=i)
        tss = daily_tss.get(d, 0.0)
        weight = (1 - decay) * (decay ** i)
        ctl += tss * weight
    return round(ctl, 2)


def calculate_tsb(ctl: float, atl: float) -> float:
    """Training Stress Balance = CTL - ATL"""
    return round(ctl - atl, 2)


def build_daily_tss_map(
    workouts: list,
    from_date: date
) -> dict[date, float]:
    """
    Buduje słownik {date: suma_tss} z listy obiektów Workout.
    Zakłada że workout ma pola: started_at (datetime), tss (float).
    """
    tss_map: dict[date, float] = {}
    for w in workouts:
        if w.tss is None:
            continue
        d = w.started_at.date()
        if d >= from_date:
            tss_map[d] = tss_map.get(d, 0.0) + w.tss
    return tss_map


def recalculate_load_metrics(
    from_date: date,
    db_session
) -> list[dict]:
    """
    Przelicza DailyLoadMetric dla zakresu od from_date do dziś.
    Pobiera treningi z ostatnich 42*3 dni dla dokładności CTL.
    Zwraca listę słowników z wynikami.
    """
    from infrastructure.db.models import Workout, DailyLoadMetric
    from datetime import datetime

    lookback_start = from_date - timedelta(days=42 * 3)

    workouts = db_session.query(Workout).filter(
        Workout.started_at >= datetime.combine(
            lookback_start, datetime.min.time()
        )
    ).all()

    daily_tss = build_daily_tss_map(workouts, lookback_start)

    today = date.today()
    results = []
    current = from_date

    while current <= today:
        tss_day = daily_tss.get(current, 0.0)
        atl = calculate_atl(daily_tss, current)
        ctl = calculate_ctl(daily_tss, current)
        tsb = calculate_tsb(ctl, atl)

        existing = db_session.query(DailyLoadMetric).filter_by(
            metric_date=current
        ).first()

        if existing:
            existing.tss_day = tss_day
            existing.atl_7d = atl
            existing.ctl_42d = ctl
            existing.tsb = tsb
        else:
            metric = DailyLoadMetric(
                metric_date=current,
                tss_day=tss_day,
                atl_7d=atl,
                ctl_42d=ctl,
                tsb=tsb,
            )
            db_session.add(metric)

        results.append({
            "date": current.isoformat(),
            "tss": tss_day,
            "atl": atl,
            "ctl": ctl,
            "tsb": tsb,
        })
        current += timedelta(days=1)

    db_session.commit()
    return results
