import numpy as np

from stats import smoothing
from time_series import time_series
from time_series.time_series import TimeSeries


def test_smooth_method_moving_average():
    tseries = TimeSeries(
        name="test fixture",
        time=time_series.gen_datetimes(step_sec=5, nb_step=5, start_datetime="2022-11-04T14:34:00+03:00"),
        resource=np.array([0, 2, -1, -2, 1]),
    )
    # Test expectation
    expected = [1, 1 / 3, -1 / 3, -2 / 3, -1 / 2]

    smoothed_ts = smoothing.moving_average(tseries, window_size=3)
    np.testing.assert_array_almost_equal_nulp(expected, smoothed_ts.resource, nulp=1)
