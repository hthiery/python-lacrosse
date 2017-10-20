#!/usr/bin/env python

import nose
import time
import threading

from nose.tools import eq_
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
            vals = [
                'OK 9 1 1 4 150 106',
                'OK 9 2 1 4 150 106',
                'OK 9 2 1 4 150 106',
            ]

            if side_effect_fct.counter >= len(vals):
                v = ""
            else:
                v = vals[side_effect_fct.counter]
            side_effect_fct.counter += 1
            return v

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

class TestLaCrosseSensor(object):

    def test_init(self):
        s = LaCrosseSensor('OK 9 1 1 4 150 66')
        eq_(s.sensorid, 1)
        eq_(s.sensortype, 1)
        eq_(s.temperature, 17.4)
        eq_(s.humidity, 66)
        eq_(s.new_battery, False)
        eq_(s.low_battery, False)
