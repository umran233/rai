import logging
from prometheus_client import start_http_server, Counter, Histogram, Gauge, Summary
import psutil
from .metrics_logger import log_metric_to_file
from datetime import datetime, timedelta
import os

# Настройка логирования
logging.basicConfig(
    filename='metrics.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

LOG_FILE = "metrics.log"
LOG_RETENTION_DAYS = 7


def clear_old_logs():
    """Удаляет строки из лога, которые старше установленного периода хранения."""
    if not os.path.exists(LOG_FILE):
        return

    retention_date = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
    updated_lines = []

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        for line in file:
            try:
                timestamp_str = line.split(" - ")[0]
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp >= retention_date:
                    updated_lines.append(line)
            except (ValueError, IndexError):
                # Если формат строки некорректен, оставляем ее
                updated_lines.append(line)

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

# Определение метрик
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint']
)

request_latency = Histogram(
    'http_request_latency_seconds',
    'Latency of HTTP requests',
    ['method', 'endpoint']
)

server_cpu_usage = Gauge(
    'server_cpu_usage_percent',
    'Current CPU usage of the server in percent'
)

server_memory_usage = Gauge(
    'server_memory_usage_percent',
    'Current memory usage of the server in percent'
)

item_method_latency = Summary(
    'item_method_latency_seconds',
    'Latency of the "Item" API method in seconds'
)

network_in_bytes = Counter(
    'network_in_bytes_total',
    'Total incoming network traffic in bytes',
    ['interface']
)

network_out_bytes = Counter(
    'network_out_bytes_total',
    'Total outgoing network traffic in bytes',
    ['interface']
)

disk_usage = Gauge(
    'disk_usage_percent',
    'Disk usage percentage',
    ['mountpoint']
)


class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        method = request.method
        endpoint = request.path

        # Логирование HTTP-запроса
        log_metric_to_file('http_requests_total', 1, labels={'method': method, 'endpoint': endpoint},
                           service_name='web_app')

        with request_latency.labels(method=method, endpoint=endpoint).time():
            response = self.get_response(request)

        http_requests_total.labels(method=method, endpoint=endpoint).inc()

        self.update_server_metrics()

        if endpoint == '/api/items/':
            with item_method_latency.time():
                pass

        return response

    @staticmethod
    def update_server_metrics():
        """Обновляет метрики сервера для мониторинга CPU, памяти, сети и диска, записывая их в лог."""
        cpu_usage = psutil.cpu_percent(interval=None)
        memory_usage = psutil.virtual_memory().percent
        server_cpu_usage.set(cpu_usage)
        server_memory_usage.set(memory_usage)

        log_metric_to_file('server_cpu_usage_percent', cpu_usage, service_name='server_monitor')
        log_metric_to_file('server_memory_usage_percent', memory_usage, service_name='server_monitor')

        network_stats = psutil.net_io_counters(pernic=True)
        for interface, stats in network_stats.items():
            network_in_bytes.labels(interface=interface).inc(stats.bytes_recv)
            network_out_bytes.labels(interface=interface).inc(stats.bytes_sent)
            log_metric_to_file('network_in_bytes_total', stats.bytes_recv, labels={'interface': interface},
                               service_name='network_monitor')
            log_metric_to_file('network_out_bytes_total', stats.bytes_sent, labels={'interface': interface},
                               service_name='network_monitor')

        disk_usage_stats = psutil.disk_partitions()
        for partition in disk_usage_stats:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_usage.labels(mountpoint=partition.mountpoint).set(usage.percent)
            log_metric_to_file('disk_usage_percent', usage.percent, labels={'mountpoint': partition.mountpoint},
                               service_name='disk_monitor')


if __name__ == "__main__":
    start_http_server(8000, addr="127.0.0.1")
    logging.info("Metrics are being served on port 8000...")

    while True:
        MetricsMiddleware.update_server_metrics()
        clear_old_logs()