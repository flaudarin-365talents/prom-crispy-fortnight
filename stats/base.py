import numpy as np


def percentiles(
    sample: list[float] | np.ndarray, percents: list[float] | float, method: str = "linear"
) -> list[float] | float:
    return np.percentile(sample, percents, method=method).tolist()
