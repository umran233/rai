import logging

# Настройка логгера
logging.basicConfig(
    filename='data/metrics.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_metric_to_file(metric_name, value, labels=None, service_name='default_service'):
    """Записывает метрики в файл."""
    labels_str = f" Labels: {labels}" if labels else ""
    log_message = f"Metric: {metric_name} | Value: {value} | Service: {service_name}{labels_str}"
    logging.info(log_message)
