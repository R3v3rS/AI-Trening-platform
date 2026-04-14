import json
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.db.models import AthleteProfile


class ProfileRepository:

    def __init__(self, db: Session):
        self.db = db

    def get(self) -> AthleteProfile | None:
        return self.db.query(AthleteProfile).filter_by(id=1).first()

    def upsert(self, data: dict) -> AthleteProfile:
        profile = self.get()

        # Serializuj listy do JSON string przed zapisem
        if "goals" in data and isinstance(data["goals"], list):
            data["goals"] = json.dumps(data["goals"])
        if (
            "preferred_training_days" in data
            and isinstance(data["preferred_training_days"], list)
        ):
            data["preferred_training_days"] = json.dumps(
                data["preferred_training_days"]
            )

        if profile is None:
            profile = AthleteProfile(id=1, **data)
            self.db.add(profile)
        else:
            for key, value in data.items():
                if value is not None:
                    setattr(profile, key, value)
            profile.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(profile)
        return profile


def profile_to_dict(profile: AthleteProfile) -> dict:
    """Serializuje profil do słownika – dekoduje JSON stringi."""
    import json

    def _decode(val):
        if isinstance(val, str):
            try:
                return json.loads(val)
            except (ValueError, TypeError):
                return val
        return val

    return {
        "ftp_watts": profile.ftp_watts,
        "weight_kg": profile.weight_kg,
        "hr_max": profile.hr_max,
        "hr_threshold": profile.hr_threshold,
        "experience_level": profile.experience_level,
        "weekly_hours": profile.weekly_hours,
        "goals": _decode(profile.goals),
        "preferred_training_days": _decode(profile.preferred_training_days),
        "max_ride_time_per_day_min": profile.max_ride_time_per_day_min,
        "indoor_vs_outdoor_preference": profile.indoor_vs_outdoor_preference,
        "updated_at": (
            profile.updated_at.isoformat() if profile.updated_at else None
        ),
    }
