import sys

from debug_helper import DebugHelper
from exceptions import MonitoringError
from logger_config import setup_logger
from module_a import SENSORS, SensorSender
from module_b import MonitorReceiver

log = setup_logger()
debug = DebugHelper(enabled="--debug" in sys.argv)

MENU = """
=== Мониторинг микроклимата серверной ===
1 - Опросить все датчики
2 - Опросить один датчик
3 - Статистика температуры
4 - Список нарушений
5 - Сохранить отчёт
0 - Выход"""


def show(data):
    print(f"{data['sensor_id']} | {data['location']}: "
          f"{data['temperature']} C, {data['humidity']} %")


def main():
    sender = SensorSender()
    receiver = MonitorReceiver()
    receive = debug.trace(receiver.receive)
    while True:
        print(MENU)
        choice = input("Выберите пункт: ").strip()
        try:
            if choice == "1":
                for sensor_id in SENSORS:
                    show(receive(sender.send(sensor_id)))
            elif choice == "2":
                sensor_id = input("ID датчика (S1-S3): ").strip().upper()
                show(receive(sender.send(sensor_id)))
            elif choice == "3":
                stats = receiver.statistics()
                debug.dump(stats, "statistics")
                print(f"Замеров: {stats['count']}, мин: {stats['t_min']}, "
                      f"макс: {stats['t_max']}, средняя: {stats['t_avg']}")
            elif choice == "4":
                print("\n".join(receiver.alarms) or "Нарушений нет")
            elif choice == "5":
                print("Отчёт сохранён:", receiver.save_report())
            elif choice == "0":
                break
            else:
                print("Неверный пункт меню")
        except MonitoringError as e:
            log.error("Ошибка: %s", e)
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
