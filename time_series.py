from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import orjson


@dataclass
class TimeSeries:
    name: str
    resource: np.ndarray
    time: list[datetime]

    def to_json(self) -> bytes:
        return orjson.dumps(
            {"name": self.name, "resource": self.resource, "time": self.time},
            option=orjson.OPT_SERIALIZE_NUMPY,
        )

    @staticmethod
    def from_json(path):
        dump_path = Path(path)
        if not dump_path.is_file:
            raise FileNotFoundError(f"File '{dump_path.absolute()}' does not exist")

        with dump_path.open("rb") as binary_io:
            data_dict: dict[str, Any] = orjson.loads(binary_io.read())

        data_dict["time"] = [
            datetime.strptime(datetime_val, "%Y-%m-%dT%H:%M:%S%z") for datetime_val in data_dict["time"]
        ]

        return TimeSeries(**data_dict)
