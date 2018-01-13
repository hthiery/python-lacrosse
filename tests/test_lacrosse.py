#!/usr/bin/env python

import time

from nose.tools import eq_, raises
from mock import MagicMock

from pylacrosse import (LaCrosse, LaCrosseSensor)

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
                'OK 9 1 1 4 150 106',
                'OK 9 2 1 4 150 106',
                'OK 9 2 1 4 150 106',
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

        l = LaCrosse('/dev/ttyTEST', 115200)
        l._serial.readline = mock_readline
        l.register_callback(1, mock_cb_1)
        l.register_callback(2, mock_cb_2)

        l._start_worker()
        time.sleep(0.01)
        l._stop_worker()

        eq_(mock_cb_1.call_count, 1)
        eq_(mock_cb_2.call_count, 2)

    def test_get_info(self):
        info = LaCrosse._parse_info('[LaCrosseITPlusReader.10.1s (RFM12B f:0 r:17241)]')
        eq_(info['name'], 'LaCrosseITPlusReader')
        eq_(info['version'], '10.1s')

        info = LaCrosse._parse_info('[LaCrosseITPlusReader.10.1s (RFM12B f:0 r:17241)]')
        eq_(info['rfm1name'], 'RFM12B')
        eq_(info['rfm1frequency'], '0')
        eq_(info['rfm1datarate'], '17241')

        info = LaCrosse._parse_info('[LaCrosseITPlusReader.10.1s (RFM12B f:0 t:10~3)]')
        eq_(info['rfm1name'], 'RFM12B')
        eq_(info['rfm1frequency'], '0')
        eq_(info['rfm1datarate'], None)
        eq_(info['rfm1toggleinterval'], '10')
        eq_(info['rfm1togglemask'], '3')

    def test_led_mode_state(self):
        mock = MagicMock()

        l = LaCrosse('/dev/ttyTEST', 115200)
        l._serial.write = mock

        l.led_mode_state(True)
        l._serial.write.assert_called_with(b'1a')

        l.led_mode_state(False)
        l._serial.write.assert_called_with(b'0a')

    def test_set_frequency(self):
        mock = MagicMock()

        l = LaCrosse('/dev/ttyTEST', 115200)
        l._serial.write = mock

        l.set_frequency(100)
        l._serial.write.assert_called_with(b'100f')

        l.set_frequency('200')
        l._serial.write.assert_called_with(b'200f')

        l.set_frequency(300, rfm=1)
        l._serial.write.assert_called_with(b'300f')

        l.set_frequency(400, rfm=2)
        l._serial.write.assert_called_with(b'400F')

    @raises(KeyError)
    def test_set_frequency_invalid_rfm(self):
        mock = MagicMock()

        l = LaCrosse('/dev/ttyTEST', 115200)
        l._serial.write = mock

        l.set_frequency(500, rfm=3)
        l._serial.write.assert_called_with(b'400f')

    def test_set_datarate(self):
        mock = MagicMock()

        l = LaCrosse('/dev/ttyTEST', 115200)
        l._serial.write = mock

        l.set_datarate(0)
        l._serial.write.assert_called_with(b'0r')
        l.set_datarate('1')
        l._serial.write.assert_called_with(b'1r')

        l.set_datarate(0, rfm=1)
        l._serial.write.assert_called_with(b'0r')
        l.set_datarate(0, rfm=2)
        l._serial.write.assert_called_with(b'0R')

    def test_set_toggle_interval(self):
        mock = MagicMock()

        l = LaCrosse('/dev/ttyTEST', 115200)
        l._serial.write = mock

        l.set_toggle_interval(10)
        l._serial.write.assert_called_with(b'10t')
        l.set_toggle_interval('10')
        l._serial.write.assert_called_with(b'10t')

        l.set_toggle_interval(10, rfm=1)
        l._serial.write.assert_called_with(b'10t')
        l.set_toggle_interval(10, rfm=2)
        l._serial.write.assert_called_with(b'10T')

    def test_set_toggle_mask(self):
        mock = MagicMock()

        l = LaCrosse('/dev/ttyTEST', 115200)
        l._serial.write = mock

        l.set_toggle_mask(1)
        l._serial.write.assert_called_with(b'1m')
        l.set_toggle_mask('1')
        l._serial.write.assert_called_with(b'1m')

        l.set_toggle_mask(2, rfm=1)
        l._serial.write.assert_called_with(b'2m')
        l.set_toggle_mask(3, rfm=2)
        l._serial.write.assert_called_with(b'3M')

class TestLaCrosseSensor(object):

    def test_init(self):
        s = LaCrosseSensor('OK 9 1 1 4 150 66')
        eq_(s.sensorid, 1)
        eq_(s.sensortype, 1)
        eq_(s.temperature, 17.4)
        eq_(s.humidity, 66)
        eq_(s.new_battery, False)
        eq_(s.low_battery, False)
