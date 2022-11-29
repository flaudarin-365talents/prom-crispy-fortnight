from prometheus import Metrics
from prometheus.prom_pod_usage_service import PromPodUsageService


def test_query_by_pod():
    # Parameters
    k8s_cluster = "preprod"
    range_from = 30  # days
    range_to = 0  # days, 0 = "now"

    prom_service = PromPodUsageService(cluster=k8s_cluster, pod_pattern="matching-worker-data-")
    res = prom_service.query_by_pod(
        pod_name="analyzer-worker-data-",
        start=range_from,
        end=range_to,
        step=30,
        metric=Metrics.CPU_LOAD,
    )
    print(res)
