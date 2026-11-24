"""Модуль-получатель: проверяет JSON, ищет нарушения, считает статистику."""
import json
from pathlib import Path

from exceptions import InvalidDataError
from logger_config import setup_logger

log = setup_logger()

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "settings.json"
REPORT_PATH = ROOT / "docs" / "monitoring_report.json"
REQUIRED = ("sensor_id", "location", "temperature", "humidity", "time")


def load_settings(path=CONFIG_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class MonitorReceiver:
    def __init__(self, settings=None):
        self.settings = settings or load_settings()
        self.readings = []
        self.alarms = []

    def receive(self, message):
        """Принимает JSON-строку, проверяет и сохраняет показание."""
        try:
            data = json.loads(message)
        except json.JSONDecodeError as e:
            raise InvalidDataError(f"Некорректный JSON: {e}") from e

        missing = [k for k in REQUIRED if k not in data]
        if missing:
            raise InvalidDataError("Нет полей: " + ", ".join(missing))
        for key in ("temperature", "humidity"):
            if not isinstance(data[key], (int, float)):
                raise InvalidDataError(f"Поле {key} должно быть числом")

        self.readings.append(data)
        self.check_limits(data)
        log.info("Получено: %s", data["sensor_id"])
        return data

    def check_limits(self, data):
        s, t, h = self.settings, data["temperature"], data["humidity"]
        if t > s["temp_max"]:
            self._alarm(data, f"температура {t} выше нормы ({s['temp_max']})")
        elif t < s["temp_min"]:
            self._alarm(data, f"температура {t} ниже нормы ({s['temp_min']})")
        if h > s["humidity_max"]:
            self._alarm(data, f"влажность {h} выше нормы ({s['humidity_max']})")
        elif h < s["humidity_min"]:
            self._alarm(data, f"влажность {h} ниже нормы ({s['humidity_min']})")

    def _alarm(self, data, text):
        message = f"[{data['sensor_id']}] {text}"
        self.alarms.append(message)
        log.warning(message)

    def statistics(self):
        if not self.readings:
            raise InvalidDataError("Нет данных для статистики")
        temps = [r["temperature"] for r in self.readings]
        return {
            "count": len(temps),
            "t_min": min(temps),
            "t_max": max(temps),
            "t_avg": round(sum(temps) / len(temps), 1),
        }

    def save_report(self, path=REPORT_PATH):
        report = {"statistics": self.statistics(), "alarms": self.alarms}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        log.info("Отчёт сохранён: %s", path)
        return path
