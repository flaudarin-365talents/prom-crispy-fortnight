import matplotlib.pyplot as plt
import numpy as np

from time_series.time_series import TimeSeries


def find(time_series: TimeSeries):
    y_vals = time_series.resource
    y_diff = y_vals[1:] - y_vals[:-1]
    found = np.where(np.logical_and(y_diff[:-1] > 0, y_diff[1:] < 0))[0] + 1
    return found


class Statistics:
    @property
    def plots(self) -> "Plots":
        return self._plots

    def __init__(self, time_series: TimeSeries, indices: list[int]) -> None:
        self._time_series = time_series
        self._indices = indices
        self._plots = Plots(self)
        self._values = [self._time_series.resource[index] for index in self._indices]

    def datetimes(self, threshold=0.0):
        return [
            self._time_series.time[index] for index in self._indices if self._time_series.resource[index] > threshold
        ]

    def values(self):
        return self._values

    def percentiles(self, *percents: float, method="linear"):
        return np.percentile(self._values, percents, method=method)[0]


class Plots:
    def __init__(self, statistics: Statistics) -> None:
        self._statistics = statistics

    def histogram(self, bins=10, xlim=None):
        fig, ax = plt.subplots()

        ax.hist(self._statistics.values(), bins=bins, linewidth=0.5, edgecolor="white")
        if xlim:
            ax.set(xlim=xlim)

        plt.show()
