from dataclasses import dataclass
from typing import Optional
from datetime import date


VALID_WORKOUT_TYPES = {
    "z2", "tempo", "vo2max", "recovery", "long_ride", "ftp_test"
}
VALID_STATUSES = {"planned", "completed", "skipped", "moved"}


@dataclass
class PlannedWorkoutCreateRequest:
    planned_date: str
    type: Optional[str] = None
    duration_sec: Optional[int] = None
    target_zone: Optional[str] = None
    notes: Optional[str] = None
    structured_steps: Optional[str] = None

    def validate(self) -> dict[str, str]:
        errors = {}

        try:
            date.fromisoformat(self.planned_date)
        except (ValueError, TypeError):
            errors["planned_date"] = "Format daty: YYYY-MM-DD"

        if self.type is not None and self.type not in VALID_WORKOUT_TYPES:
            errors["type"] = (
                f"Dozwolone wartości: {sorted(VALID_WORKOUT_TYPES)}"
            )

        if self.duration_sec is not None and self.duration_sec <= 0:
            errors["duration_sec"] = "Musi być większe niż 0"

        return errors

    @classmethod
    def from_dict(cls, data: dict) -> "PlannedWorkoutCreateRequest":
        return cls(
            planned_date=data.get("planned_date", ""),
            type=data.get("type"),
            duration_sec=data.get("duration_sec"),
            target_zone=data.get("target_zone"),
            notes=data.get("notes"),
            structured_steps=data.get("structured_steps"),
        )


@dataclass
class StatusUpdateRequest:
    status: str
    moved_to_date: Optional[str] = None

    def validate(self) -> dict[str, str]:
        errors = {}

        if self.status not in VALID_STATUSES:
            errors["status"] = (
                f"Dozwolone wartości: {sorted(VALID_STATUSES)}"
            )

        if self.status == "moved":
            if not self.moved_to_date:
                errors["moved_to_date"] = (
                    "Wymagane gdy status=moved"
                )
            else:
                try:
                    date.fromisoformat(self.moved_to_date)
                except ValueError:
                    errors["moved_to_date"] = "Format daty: YYYY-MM-DD"

        return errors

    @classmethod
    def from_dict(cls, data: dict) -> "StatusUpdateRequest":
        return cls(
            status=data.get("status", ""),
            moved_to_date=data.get("moved_to_date"),
        )
