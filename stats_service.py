from time_series import TimeSeries


class StatsService:
    @property
    def name(self):
        return self._name

    @property
    def time_series(self) -> TimeSeries:
        return self._time_series

    def __init__(self, name: str) -> None:
        self._name = name
        self._time_series: TimeSeries = None

    def load_time_series(self, path: str):
        """_summary_

        Args:
            path (str): path to the dump file of the time series
        """
        self._time_series = TimeSeries.from_json(path)
