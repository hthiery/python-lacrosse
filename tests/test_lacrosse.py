#!/usr/bin/env python

import time
from unittest.mock import MagicMock

import pytest

from pylacrosse import LaCrosse, LaCrosseSensor


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


class TestLacrosse(object):
    def test_refresh(self):
        mock_readline = MagicMock()

        def side_effect_fct():
            if not hasattr(side_effect_fct, "counter"):
                side_effect_fct.counter = 0
            values = [
                "OK 9 1 1 4 150 106",
                "OK 9 2 1 4 150 106",
                "OK 9 2 1 4 150 106",
            ]

            if side_effect_fct.counter >= len(values):
                value = ""
            else:
                value = values[side_effect_fct.counter]
            side_effect_fct.counter += 1
            return value

        mock_readline.side_effect = side_effect_fct

        mock_cb_1 = MagicMock(return_value=None)
        mock_cb_2 = MagicMock(return_value=None)

        lacrosse = LaCrosse("/dev/ttyTEST", 115200)
        lacrosse._serial.readline = mock_readline
        lacrosse.register_callback(1, mock_cb_1)
        lacrosse.register_callback(2, mock_cb_2)

        lacrosse._start_worker()
        time.sleep(0.01)
        lacrosse._stop_worker()

        assert mock_cb_1.call_count == 1
        assert mock_cb_2.call_count == 2

    def test_get_info(self):
        info = LaCrosse._parse_info("[LaCrosseITPlusReader.10.1s (RFM12B f:0 r:17241)]")
        assert info["name"] == "LaCrosseITPlusReader"
        assert info["version"] == "10.1s"

        info = LaCrosse._parse_info("[LaCrosseITPlusReader.10.1s (RFM12B f:0 r:17241)]")
        assert info["rfm1name"] == "RFM12B"
        assert info["rfm1frequency"] == "0"
        assert info["rfm1datarate"] == "17241"

        info = LaCrosse._parse_info("[LaCrosseITPlusReader.10.1s (RFM12B f:0 t:10~3)]")
        assert info["rfm1name"] == "RFM12B"
        assert info["rfm1frequency"] == "0"
        assert info["rfm1datarate"] is None
        assert info["rfm1toggleinterval"] == "10"
        assert info["rfm1togglemask"] == "3"

    def test_led_mode_state(self):
        mock = MagicMock()

        lacrosse = LaCrosse("/dev/ttyTEST", 115200)
        lacrosse._serial.write = mock

        lacrosse.led_mode_state(True)
        lacrosse._serial.write.assert_called_with(b"1a")

        lacrosse.led_mode_state(False)
        lacrosse._serial.write.assert_called_with(b"0a")

    def test_set_frequency(self):
        mock = MagicMock()

        lacrosse = LaCrosse("/dev/ttyTEST", 115200)
        lacrosse._serial.write = mock

        lacrosse.set_frequency(100)
        lacrosse._serial.write.assert_called_with(b"100f")

        lacrosse.set_frequency("200")
        lacrosse._serial.write.assert_called_with(b"200f")

        lacrosse.set_frequency(300, rfm=1)
        lacrosse._serial.write.assert_called_with(b"300f")

        lacrosse.set_frequency(400, rfm=2)
        lacrosse._serial.write.assert_called_with(b"400F")

    def test_set_frequency_invalid_rfm(self):
        mock = MagicMock()

        lacrosse = LaCrosse("/dev/ttyTEST", 115200)
        lacrosse._serial.write = mock

        with pytest.raises(KeyError):
            lacrosse.set_frequency(500, rfm=3)
            lacrosse._serial.write.assert_called_with(b"400f")

    def test_set_datarate(self):
        mock = MagicMock()

        lacrosse = LaCrosse("/dev/ttyTEST", 115200)
        lacrosse._serial.write = mock

        lacrosse.set_datarate(0)
        lacrosse._serial.write.assert_called_with(b"0r")
        lacrosse.set_datarate("1")
        lacrosse._serial.write.assert_called_with(b"1r")

        lacrosse.set_datarate(0, rfm=1)
        lacrosse._serial.write.assert_called_with(b"0r")
        lacrosse.set_datarate(0, rfm=2)
        lacrosse._serial.write.assert_called_with(b"0R")

    def test_set_toggle_interval(self):
        mock = MagicMock()

        lacrosse = LaCrosse("/dev/ttyTEST", 115200)
        lacrosse._serial.write = mock

        lacrosse.set_toggle_interval(10)
        lacrosse._serial.write.assert_called_with(b"10t")
        lacrosse.set_toggle_interval("10")
        lacrosse._serial.write.assert_called_with(b"10t")

        lacrosse.set_toggle_interval(10, rfm=1)
        lacrosse._serial.write.assert_called_with(b"10t")
        lacrosse.set_toggle_interval(10, rfm=2)
        lacrosse._serial.write.assert_called_with(b"10T")

    def test_set_toggle_mask(self):
        mock = MagicMock()

        lacrosse = LaCrosse("/dev/ttyTEST", 115200)
        lacrosse._serial.write = mock

        lacrosse.set_toggle_mask(1)
        lacrosse._serial.write.assert_called_with(b"1m")
        lacrosse.set_toggle_mask("1")
        lacrosse._serial.write.assert_called_with(b"1m")

        lacrosse.set_toggle_mask(2, rfm=1)
        lacrosse._serial.write.assert_called_with(b"2m")
        lacrosse.set_toggle_mask(3, rfm=2)
        lacrosse._serial.write.assert_called_with(b"3M")


class TestLaCrosseSensor(object):
    def test_init(self):
        s = LaCrosseSensor("OK 9 1 1 4 150 66")
        assert s.sensorid == 1
        assert s.sensortype == 1
        assert s.temperature == 17.4
        assert s.humidity == 66
        assert not s.new_battery
        assert not s.low_battery
