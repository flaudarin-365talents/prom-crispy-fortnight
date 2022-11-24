import numpy as np

from stats.base import percentiles


def test_percentiles():
    sample = np.random.random(1000)
    res = percentiles(sample, [50, 75, 95])
    assert len(res) == 3

    res = percentiles(sample, [50])
    assert len(res) == 1

    res = percentiles(sample, 50)
    assert isinstance(res, float)
