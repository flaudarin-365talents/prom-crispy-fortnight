import sys
from datetime import datetime
from enum import Enum
from pathlib import Path

import numpy as np
from dateutil import tz
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.exceptions import PrometheusApiClientException
from prometheus_api_client.utils import parse_datetime

from time_series import TimeSeries

# Maximal number of days that can be queried with a minimal timestep of 30s
PROM_MAX_DAYS = 3


class PromUsageService:
    class Metrics(Enum):
        CPU_LOAD = "cpu load"
        MEMORY_MIB = "memory MiB"

    def __init__(self, cluster="preprod", workload="analyzer-worker-data") -> None:
        self._cluster = cluster
        self._workload = workload
        self._url = f"http://prometheus-{self._cluster}.int.365talents.com"
        self._prom_api_service = PrometheusConnect(url=self._url)
        # For caching the last data extraction
        self._data_cache: TimeSeries | None = None
        self._data_metric: PromUsageService.Metrics | None = None

    def _get_promql_query(self, metric: "PromUsageService.Metrics"):
        promql_queries = {
            PromUsageService.Metrics.CPU_LOAD: f"""
            sum(
              node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{{namespace="default"}}
              * on(namespace,pod)
              group_left(workload, workload_type)
              namespace_workload_pod:kube_pod_owner:relabel{{
                namespace="default",
                workload="{self._workload}"
              }}
            ) by (workload, workload_type)
            """,
            PromUsageService.Metrics.MEMORY_MIB: f"""
            sum(
              container_memory_working_set_bytes{{
                namespace="default",
                container!="",
                image!="",
                metrics_path="/metrics/cadvisor"
              }}
              * on(namespace, pod)
              group_left(workload, workload_type)
              namespace_workload_pod:kube_pod_owner:relabel{{
                namespace="default",
                workload_type="statefulset",
                workload="{self._workload}"
              }}
            ) by (workload, workload_type)
            """,
        }
        return promql_queries[metric]

    def query(
        self, start: int, end: int = 0, step: int = 30, metric: "PromUsageService.Metrics" = Metrics.CPU_LOAD
    ) -> "TimeSeries":
        prom_ql_query = self._get_promql_query(metric)

        # List of bounds of queries: starts with 1 one query
        query_plan = [(start, end)]

        def prom_time_format(days: int):
            return "now" if days == 0 else f"{days}d"

        query_results = []

        while query_plan:
            queried_start_day, queried_end_day = query_plan.pop(0)
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
                print(f"Split extraction into {len(query_plan)} chunks")
            print(f"Remaining chunks to extract: {len(query_plan)}")

        # Aggregation of query results and extraction
        aggregated_results = []
        for res in reversed(query_results):
            aggregated_results.extend(res[0]["values"])
        data = np.array(aggregated_results, dtype=np.float64)

        # plot
        tzone = tz.gettz("Etc/GMT-3")
        time_steps = [datetime.fromtimestamp(step, tz=tzone) for step in data[:, 0]]
        # Casts to C-contiguous array for preventing orsjon to complain while serializing
        metric_values = np.ascontiguousarray(data[:, 1])

        if metric == PromUsageService.Metrics.MEMORY_MIB:
            metric_values *= 2**-20

        self._data_cache = TimeSeries(name=metric.value, resource=metric_values, time=time_steps)

        return self._data_cache

    def save_cache(self, path: str, overwrite=False):
        save_path = Path(path)
        if self._data_cache is None:
            print("No cached data to save")
            return

        if save_path.is_file() and not overwrite:
            sys.stderr.write(f"File {save_path} already exists")
            sys.stderr.flush()
            return

        with save_path.open("wb") as binary_io:
            binary_io.write(self._data_cache.to_json())

        print(f"Saved cached data to:\n'{save_path.absolute()}'")
