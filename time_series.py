from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import orjson
from scipy.interpolate import interp1d

DATETIME_FMT = r"%Y-%m-%dT%H:%M:%S%z"


class TimeSeries:
    name: str
    resource: np.ndarray
    time: list[datetime]

    def __init__(self, name: str, time: list[datetime], resource: np.ndarray) -> None:
        if len(time) != resource.shape[0]:
            raise ValueError("'time' and 'resource' length mismatch")
        self.name = name
        self.time = time
        self.resource = resource
        self.prune_duplicates()

    def prune_duplicates(self) -> "TimeSeries":
        previous_datetime = None
        deletion_indices = []
        for index, dt in enumerate(self.time):
            if previous_datetime and previous_datetime == dt:
                deletion_indices.append(index)
            previous_datetime = dt

        deletion_indices.reverse()
        for index in deletion_indices:
            del self.time[index]
        self.resource = np.delete(self.resource, deletion_indices)

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
        data_dict["resource"] = np.array(data_dict["resource"])

        return TimeSeries(**data_dict)

    def interpolate(self, step_sec: int, in_place=False) -> "TimeSeries":
        """_summary_

        Args:
            step_sec (int): interpolation time step (seconds)
            in_place (bool, optional): the time series is updated if True. Defaults to False.

        Returns:
            TimeSeries: interpolated time series
        """

        def datetimes_to_vect(dt_list: list[datetime]):
            return np.array([int(dt.timestamp()) for dt in dt_list])

        nb_step = (int(self.time[-1].timestamp()) - int(self.time[0].timestamp())) // step_sec

        dt_interp = gen_datetimes(step_sec, nb_step, start_datetime=self.time[0])
        dt_interp.append(self.time[-1])

        dt_interp_vect = datetimes_to_vect(dt_interp)
        dt_vect = datetimes_to_vect(self.time)

        interpolate_func = interp1d(dt_vect, self.resource, kind="quadratic")
        val_interp_vect = interpolate_func(dt_interp_vect)

        if in_place:
            self.time = dt_interp
            self.resource = val_interp_vect
            return self
        else:
            return TimeSeries(
                name=self.name + " (interpolation)",
                resource=val_interp_vect,
                time=dt_interp,
            )


def gen_datetimes(step_sec: int, nb_step: int, start_datetime: str | datetime = "2022-11-04T14:34:00+03:00"):
    if isinstance(start_datetime, str):
        start_datetime = datetime.strptime(start_datetime, DATETIME_FMT)
    return [start_datetime + timedelta(seconds=step_offset * step_sec) for step_offset in range(nb_step)]
