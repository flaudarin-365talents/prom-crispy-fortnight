from datetime import datetime

import numpy as np
import numpy.testing as np_t

from time_series import time_series
from time_series.time_series import TimeSeries


def test_interpolation():
    tseries = TimeSeries(
        name="test",
        resource=np.array([0, 1, 3, 2, -1, 0]),
        time=time_series.gen_datetimes(step_sec=30, nb_step=6, start_datetime="2022-11-25T15:30:00+03:00"),
    )
    np_t.assert_almost_equal(
        tseries.interpolate(step_sec=15, in_place=True).resource,
        [0.0, 0.28921569, 1.0, 2.13235294, 3.0, 2.91666667, 2.0, 0.36764706, -1.0, -1.12254902, 0.0],
        decimal=8,
    )


def test_prune_duplicates():
    datetime_values = time_series.gen_datetimes(step_sec=30, nb_step=5, start_datetime="2022-11-25T15:30:00+03:00")
    pruned_datetime_values = datetime_values.copy()
    pruned_resource_values = np.array([0, 1, 2, -1, 0])

    datetime_values.insert(3, datetime_values[3])
    datetime_values.insert(1, datetime_values[1])

    tseries = TimeSeries(
        name="test",
        resource=np.array([0, 1, 1.1, 2, -1, -1, 0]),
        time=datetime_values,
    )
    assert tseries.time == pruned_datetime_values
    np.testing.assert_array_almost_equal_nulp(tseries.resource, pruned_resource_values)


def test_gen_datetimes():
    assert [
        datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z")
        for dt_str in (
            "2022-11-04T14:34:00+03:00",
            "2022-11-04T14:34:05+03:00",
            "2022-11-04T14:34:10+03:00",
            "2022-11-04T14:34:15+03:00",
            "2022-11-04T14:34:20+03:00",
        )
    ] == time_series.gen_datetimes(step_sec=5, nb_step=5, start_datetime="2022-11-04T14:34:00+03:00")
