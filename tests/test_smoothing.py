from datetime import datetime

import numpy as np

from stats import smoothing
from time_series import TimeSeries


def test_smooth_method_moving_average():
    time_series = TimeSeries(
        name="test fixture",
        time=[
            datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z")
            for dt_str in (
                "2022-11-04T14:34:00+03:00",
                "2022-11-04T14:34:05+03:00",
                "2022-11-04T14:34:10+03:00",
                "2022-11-04T14:34:15+03:00",
                "2022-11-04T14:34:20+03:00",
            )
        ],
        resource=np.array([0, 2, -1, -2, 1]),
    )

    test_ref = [1, 1 / 3, -1 / 3, -2 / 3, -1 / 2]

    smoothed_ts = smoothing.moving_average(time_series, window_size=3)
    np.testing.assert_array_almost_equal_nulp(test_ref, smoothed_ts.resource, nulp=1)
