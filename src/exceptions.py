class MonitoringError(Exception):
    """Базовое исключение системы мониторинга."""


class InvalidDataError(MonitoringError):
    """Получены некорректные данные (не JSON, нет полей, неверный тип)."""


class SensorOfflineError(MonitoringError):
    """Датчик не найден или недоступен."""
