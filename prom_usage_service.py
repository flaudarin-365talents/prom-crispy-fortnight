from dataclasses import dataclass
from datetime import datetime

import numpy as np
from dateutil import tz
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.exceptions import PrometheusApiClientException
from prometheus_api_client.utils import parse_datetime

# Maximal number of days that can be queried with a minimal timestep of 30s
PROM_MAX_DAYS = 3


class PromUsageService:
    @dataclass
    class TimeSeries:
        time: list[datetime]
        resource: np.ndarray

    def __init__(self, cluster="preprod", workload="analyzer-worker-data") -> None:
        self._cluster = cluster
        self._workload = workload
        self._url = f"http://prometheus-{self._cluster}.int.365talents.com"
        self._prom_api_service = PrometheusConnect(url=self._url)

    def query(self, start: int, end: int = 0, step: int = 30) -> "PromUsageService.TimeSeries":
        prom_ql_query = f"""
        sum(
          node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{{namespace="default"}}
          * on(namespace,pod)
          group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{{
            namespace="default",
            workload="{self._workload}"
          }}
        ) by (workload, workload_type)
        """
        # List of bounds of queries: starts with 1 one query
        query_plan = [(start, end)]

        def prom_time_format(days: int):
            return "now" if days == 0 else f"{days}d"

        query_results = []

        while query_plan:
            queried_start_day, queried_end_day = query_plan.pop(0)
            print("(queried_start_day, queried_end_day)", queried_start_day, queried_end_day)
            try:
                res = self._prom_api_service.custom_query_range(
                    query=prom_ql_query,
                    start_time=parse_datetime(prom_time_format(queried_start_day)),
                    end_time=parse_datetime(prom_time_format(queried_end_day)),
                    step=step,
                )
                query_results.append(res)
            except PrometheusApiClientException as err:
                if "exceeded maximum resolution" not in err.args[0]:
                    raise err
                assert start - end >= PROM_MAX_DAYS

                # Query time range is too long and must be split in several queries
                query_plan = []
                day_end = queried_end_day
                day_range = queried_start_day - queried_end_day
                for _ in range(day_range // PROM_MAX_DAYS):
                    query_plan.append((day_end + PROM_MAX_DAYS, day_end))
                    day_end += PROM_MAX_DAYS
                day_remainder = day_range % PROM_MAX_DAYS
                if day_remainder > 0:
                    query_plan.append((day_end + day_remainder, day_end))
                print(query_plan)

        # Aggregation of query results and extraction
        aggregated_results = []
        for res in reversed(query_results):
            aggregated_results.extend(res[0]["values"])
        data = np.array(aggregated_results, dtype=np.float64)

        # plot
        tzone = tz.gettz("Etc/GMT-3")
        time_steps = [datetime.fromtimestamp(step, tz=tzone) for step in data[:, 0]]
        cpu_usage = data[:, 1]

        return PromUsageService.TimeSeries(time=time_steps, resource=cpu_usage)
