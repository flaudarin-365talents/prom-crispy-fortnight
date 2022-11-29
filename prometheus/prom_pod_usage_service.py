from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime

from prometheus import Metrics
from time_series.time_series import TimeSeries


class PromPodUsageService:
    def __init__(self, cluster: str, pod_pattern: str) -> None:
        self._cluster = cluster
        self._pod_pattern = pod_pattern
        self._url = f"http://prometheus-{self._cluster}.int.365talents.com"
        self._prom_api_service = PrometheusConnect(url=self._url)
        # For caching the last data extraction
        self._data_cache: TimeSeries | None = None
        self._data_metric: Metrics | None = None

    def _get_promql_pod_query(self, metric: Metrics):
        promql_pod_queries = {
            Metrics.CPU_LOAD: f"""
            sum(
                node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{{
                    namespace="default",
                    pod=~"{self._pod_pattern}.+"
                }}) by (pod)
            """
        }
        return promql_pod_queries[metric]

    def query_by_pod(
        self,
        pod_name: str,
        start: int,
        end: int = 0,
        step: int = 30,
        metric: Metrics = Metrics.CPU_LOAD,
    ) -> TimeSeries:
        prom_ql_query = self._get_promql_pod_query(metric)
        res = self._prom_api_service.custom_query_range(
            query=prom_ql_query,
            start_time=parse_datetime("now-1h"),
            end_time=parse_datetime("now"),
            step=str(step),
        )
        return res
