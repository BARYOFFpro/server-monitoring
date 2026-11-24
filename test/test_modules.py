import json
import random

import pytest

from exceptions import InvalidDataError, SensorOfflineError
from module_a import SensorSender
from module_b import MonitorReceiver

SETTINGS = {"temp_max": 27.0, "temp_min": 18.0,
            "humidity_max": 60.0, "humidity_min": 30.0}


def make_message(temp=22.0, hum=45.0):
    return json.dumps({"sensor_id": "S1", "location": "Стойка 1",
                       "temperature": temp, "humidity": hum,
                       "time": "2026-11-24 10:00:00"})


def test_sender_returns_valid_json():
    msg = SensorSender(rng=random.Random(1)).send("S1")
    assert json.loads(msg)["sensor_id"] == "S1"


def test_sender_unknown_sensor():
    with pytest.raises(SensorOfflineError):
        SensorSender().send("S9")


def test_receive_valid_message():
    r = MonitorReceiver(SETTINGS)
    assert r.receive(make_message())["temperature"] == 22.0


def test_receive_invalid_json():
    with pytest.raises(InvalidDataError):
        MonitorReceiver(SETTINGS).receive("не json")


def test_receive_missing_field():
    with pytest.raises(InvalidDataError):
        MonitorReceiver(SETTINGS).receive('{"sensor_id": "S1"}')


def test_receive_temperature_as_string():
    with pytest.raises(InvalidDataError):
        MonitorReceiver(SETTINGS).receive(make_message(temp="25"))


def test_alarm_on_high_temperature():
    r = MonitorReceiver(SETTINGS)
    r.receive(make_message(temp=30.5))
    assert len(r.alarms) == 1


def test_no_alarm_in_normal_range():
    r = MonitorReceiver(SETTINGS)
    r.receive(make_message())
    assert r.alarms == []


def test_statistics():
    r = MonitorReceiver(SETTINGS)
    for t in (20.0, 22.0, 26.0):
        r.receive(make_message(temp=t))
    assert r.statistics() == {"count": 3, "t_min": 20.0,
                              "t_max": 26.0, "t_avg": 22.7}


def test_statistics_without_data():
    with pytest.raises(InvalidDataError):
        MonitorReceiver(SETTINGS).statistics()


def test_save_report(tmp_path):
    r = MonitorReceiver(SETTINGS)
    r.receive(make_message(temp=29.0))
    path = r.save_report(tmp_path / "report.json")
    assert json.loads(path.read_text(encoding="utf-8"))["alarms"]
