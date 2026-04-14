import hashlib
from datetime import datetime
from typing import Optional

import fitdecode


class FitParseError(Exception):
    pass


class GarminFitParser:
    def parse(self, file_path: str) -> dict:
        header: dict = {}
        samples: list[dict] = []
        started_at: Optional[datetime] = None

        try:
            with fitdecode.FitReader(file_path) as fit:
                for frame in fit:
                    if not isinstance(frame, fitdecode.FitDataMessage):
                        continue

                    if frame.name == "session":
                        started_at = self._get_field(frame, "start_time")
                        header = {
                            "started_at": started_at,
                            "duration_sec": self._get_field(frame, "total_timer_time"),
                            "distance_m": self._get_field(frame, "total_distance"),
                            "avg_power": self._get_field(frame, "avg_power"),
                            "avg_hr": self._get_field(frame, "avg_heart_rate"),
                            "max_power": self._get_field(frame, "max_power"),
                            "max_hr": self._get_field(frame, "max_heart_rate"),
                            "calories": self._get_field(frame, "total_calories"),
                        }

                    if frame.name == "record":
                        sample_ts = self._get_field(frame, "timestamp")
                        samples.append(
                            {
                                "timestamp": sample_ts,
                                "sec_from_start": self._seconds_from_start(started_at, sample_ts),
                                "power": self._get_field(frame, "power"),
                                "heart_rate": self._get_field(frame, "heart_rate"),
                                "cadence": self._get_field(frame, "cadence"),
                                "speed": self._get_field(frame, "speed"),
                                "distance": self._get_field(frame, "distance"),
                            }
                        )
        except Exception as exc:
            raise FitParseError(f"Could not parse FIT file: {exc}") from exc

        if not samples and not header:
            raise FitParseError("FIT file does not contain session or record data")

        return {
            "file_hash": self._sha256(file_path),
            "header": header,
            "samples": samples,
        }

    def _get_field(self, frame: fitdecode.FitDataMessage, field_name: str):
        return frame.get_value(field_name)

    def _seconds_from_start(
        self,
        started_at: Optional[datetime],
        timestamp: Optional[datetime],
    ) -> Optional[int]:
        if not started_at or not timestamp:
            return None
        return int((timestamp - started_at).total_seconds())

    def _sha256(self, file_path: str) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
