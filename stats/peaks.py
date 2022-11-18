import numpy as np

from time_series import TimeSeries


def find(time_series: TimeSeries):
    y_vals = time_series.resource
    y_diff = y_vals[1:] - y_vals[:-1]
    found = np.where(np.logical_and(y_diff[:-1] > 0, y_diff[1:] < 0))[0] + 1
    return found


class Statistics:
    def __init__(self, time_series: TimeSeries, indices: list[int]) -> None:
        self._time_series = time_series
        self._indices = indices

    def datetimes(self, threshold=0.0):
        return [
            self._time_series.time[index] for index in self._indices if self._time_series.resource[index] > threshold
        ]
