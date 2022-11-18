from datetime import datetime

import numpy as np

from stats import peaks
from time_series import TimeSeries


def test_find_peaks():
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
                "2022-11-04T14:34:25+03:00",
                "2022-11-04T14:34:30+03:00",
            )
        ],
        resource=np.array([-1, 2, 4, 1, 2, -1, 0]),
    )

    # Test expectation
    expected = [2, 4]

    peaks_found = peaks.find(time_series)
    np.testing.assert_array_almost_equal_nulp(expected, peaks_found, nulp=1)
