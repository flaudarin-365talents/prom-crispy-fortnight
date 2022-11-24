from enum import Enum

import numpy as np

from time_series import TimeSeries


class Method(Enum):
    MOVING_AVG = "moving average"


def moving_average(time_series: TimeSeries, window_size: int) -> TimeSeries:
    # The window size must be an odd integer
    if window_size % 2 == 0:
        raise ValueError(f"Argument 'window_size' must be odd: {window_size}")

    series_length = time_series.resource.shape[0]

    values = np.zeros(shape=(series_length,))
    sum_count = np.zeros(shape=(series_length,))
    half_window_size = (window_size - 1) // 2

    for index in range(series_length):
        index0 = max(0, index - half_window_size)
        index1 = min(series_length - 1, index + half_window_size)
        values[index] += time_series.resource[index0 : index1 + 1].sum()
        sum_count[index] += index1 - index0 + 1

    time_series.resource = values / sum_count

    return time_series
