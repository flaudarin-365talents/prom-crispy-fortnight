import numpy as np

Vector = list[float] | np.ndarray


def percentiles(sample: Vector, percents: list[float] | float, method: str = "linear") -> list[float] | float:
    return np.percentile(sample, percents, method=method).tolist()
