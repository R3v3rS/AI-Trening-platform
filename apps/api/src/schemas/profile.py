import json
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


VALID_EXPERIENCE_LEVELS = {"beginner", "intermediate", "advanced"}
VALID_INDOOR_OUTDOOR = {"indoor", "outdoor", "mixed"}
VALID_TRAINING_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}


@dataclass
class ProfileUpdateRequest:
    ftp_watts: Optional[int] = None
    weight_kg: Optional[float] = None
    hr_max: Optional[int] = None
    hr_threshold: Optional[int] = None
    experience_level: Optional[str] = None
    weekly_hours: Optional[float] = None
    goals: Optional[list[str]] = None
    preferred_training_days: Optional[list[str]] = None
    max_ride_time_per_day_min: Optional[int] = None
    indoor_vs_outdoor_preference: Optional[str] = None

    def validate(self) -> dict[str, str]:
        errors = {}

        if self.ftp_watts is not None and self.ftp_watts <= 0:
            errors["ftp_watts"] = "Musi być większe niż 0"

        if self.weight_kg is not None and self.weight_kg <= 0:
            errors["weight_kg"] = "Musi być większe niż 0"

        if self.hr_max is not None and self.hr_max <= 0:
            errors["hr_max"] = "Musi być większe niż 0"

        if self.hr_threshold is not None and self.hr_threshold <= 0:
            errors["hr_threshold"] = "Musi być większe niż 0"

        if (
            self.hr_max is not None
            and self.hr_threshold is not None
            and self.hr_max <= self.hr_threshold
        ):
            errors["hr_max"] = "hr_max musi być większe niż hr_threshold"

        if (
            self.experience_level is not None
            and self.experience_level not in VALID_EXPERIENCE_LEVELS
        ):
            errors["experience_level"] = (
                f"Dozwolone wartości: {sorted(VALID_EXPERIENCE_LEVELS)}"
            )

        if (
            self.indoor_vs_outdoor_preference is not None
            and self.indoor_vs_outdoor_preference not in VALID_INDOOR_OUTDOOR
        ):
            errors["indoor_vs_outdoor_preference"] = (
                f"Dozwolone wartości: {sorted(VALID_INDOOR_OUTDOOR)}"
            )

        if self.preferred_training_days is not None:
            invalid = [
                d for d in self.preferred_training_days
                if d not in VALID_TRAINING_DAYS
            ]
            if invalid:
                errors["preferred_training_days"] = (
                    f"Nieprawidłowe dni: {invalid}. "
                    f"Dozwolone: {sorted(VALID_TRAINING_DAYS)}"
                )

        if (
            self.weekly_hours is not None
            and self.weekly_hours <= 0
        ):
            errors["weekly_hours"] = "Musi być większe niż 0"

        if (
            self.max_ride_time_per_day_min is not None
            and self.max_ride_time_per_day_min <= 0
        ):
            errors["max_ride_time_per_day_min"] = "Musi być większe niż 0"

        return errors

    @classmethod
    def from_dict(cls, data: dict) -> "ProfileUpdateRequest":
        return cls(
            ftp_watts=data.get("ftp_watts"),
            weight_kg=data.get("weight_kg"),
            hr_max=data.get("hr_max"),
            hr_threshold=data.get("hr_threshold"),
            experience_level=data.get("experience_level"),
            weekly_hours=data.get("weekly_hours"),
            goals=data.get("goals"),
            preferred_training_days=data.get("preferred_training_days"),
            max_ride_time_per_day_min=data.get("max_ride_time_per_day_min"),
            indoor_vs_outdoor_preference=data.get(
                "indoor_vs_outdoor_preference"
            ),
        )
