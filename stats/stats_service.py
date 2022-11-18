from stats import smoothing
from time_series import TimeSeries


class StatsService:
    @property
    def name(self):
        return self._name

    def __init__(self, name: str) -> None:
        self._name = name
        self.time_series: TimeSeries = None

    def load_time_series(self, path: str):
        """_summary_

        Args:
            path (str): path to the dump file of the time series
        """
        self.time_series = TimeSeries.from_json(path)

    def smooth(self, algo_type: smoothing.Method = smoothing.Method.MOVING_AVG, window_size: int = 3) -> "StatsService":
        if algo_type == smoothing.Method.MOVING_AVG:
            self.time_series = smoothing.moving_average(time_series=self.time_series, window_size=window_size)
        else:
            raise ValueError(f"Unknown method {algo_type}")
