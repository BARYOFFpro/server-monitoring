"""Модуль-отправитель: снимает показания датчиков и формирует JSON."""
import json
import random
from datetime import datetime

from exceptions import SensorOfflineError
from logger_config import setup_logger

log = setup_logger()

SENSORS = {
    "S1": "Серверная, стойка 1",
    "S2": "Серверная, стойка 2",
    "S3": "Машинный зал",
}


class SensorSender:
    def __init__(self, sensors=None, rng=None):
        self.sensors = sensors or SENSORS
        self.rng = rng or random.Random()

    def read(self, sensor_id):
        """Имитирует опрос датчика, возвращает словарь с показаниями."""
        if sensor_id not in self.sensors:
            raise SensorOfflineError(f"Датчик {sensor_id} не найден")
        return {
            "sensor_id": sensor_id,
            "location": self.sensors[sensor_id],
            "temperature": round(self.rng.uniform(18, 32), 1),
            "humidity": round(self.rng.uniform(30, 70), 1),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def send(self, sensor_id):
        """Возвращает показания в виде JSON-строки (формат обмена)."""
        message = json.dumps(self.read(sensor_id), ensure_ascii=False)
        log.info("Отправлено: %s", message)
        return message
