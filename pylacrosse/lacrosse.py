# Pure python VXI-11 client
# Copyright (c) 2017 Heiko Thiery
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

import logging
import re
from serial import Serial
import threading
import time

_LOGGER = logging.getLogger(__name__)

class LaCrosse(object):

    sensors = {}
    _registry = {}

    def __init__(self, port, baud, timeout=2):
        self._port = port
        self._baud = baud
        self._timeout = timeout

    def open(self):
        self._serial = Serial(self._port, self._baud, timeout=self._timeout)
        self._serial.flushInput()
        self._serial.flushOutput()
        self._start_worker()

    def close(self):
        self._stopevent.set()
        self._thread.join()
        self._serial.close()

    def _start_worker(self):
        self._stopevent = threading.Event()
        self._thread = threading.Thread(target=self._refresh, args=())
        self._thread.daemon = True
        self._thread.start()

    def _refresh(self):
        """Background refreshing thread."""

        while not self._stopevent.isSet():
            line = self._serial.readline()
            if LaCrosseSensor.re_reading.match(line):
                sensor = LaCrosseSensor(line)
                self.sensors[sensor.sensorid] = sensor

                if sensor.sensorid in self._registry:
                    for cb in self._registry[sensor.sensorid]:
                        cb(sensor)

    def register_callback(self, sensorid, cb):
        if sensorid not in self._registry:
            self._registry[sensorid] = list()
        self._registry[sensorid].append(cb)


class LaCrosseSensor(object):
    # OK 9 248 1 4 150 106
    re_reading = re.compile('OK (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)')

    def __init__(self, line=None):
        if line:
            self._parse(line)

    def _parse(self, line):
        match = self.re_reading.match(line)
        if match:
            data = [int(c) for c in match.group().split()[1:]]
            self.sensorid = data[1]
            self.sensortype = data[2] & 0x7f
            self.new_battery = True if data[2] & 0x80 else False
            self.temperature = float(data[3] * 256 + data[4] - 1000) / 10
            self.humidity = data[5] & 0x7f
            self.low_battery = True if data[5] & 0x80 else False

    def __repr__(self):
        return "id=%d t=%f h=%d nbat=%d" % \
            (self.sensorid, self.temperature, self.humidity, self.new_battery)


def test_cb(sensor):
    print sensor

if __name__ == '__main__':

    l = LaCrosse('/dev/ttyUSB0', 56700)
    l.open()
    l.registry_callback(0, test_cb)

    while True:
        time.sleep(1)
