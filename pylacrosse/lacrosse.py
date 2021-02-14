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

from __future__ import unicode_literals
import logging
import re
import threading
import time

_LOGGER = logging.getLogger(__name__)

"""
    Jeelink lacrosse firmware commands
    <n>a     set to 0 if the blue LED bothers
    <n>f     initial frequency in kHz (5 kHz steps, 860480 ... 879515)  (for RFM
    #1)
    <n>F     initial frequency in kHz (5 kHz steps, 860480 ... 879515)  (for RFM
    #2)
    <n>h     altituide above sea level
    <n>m     bits 1: 17.241 kbps, 2 : 9.579 kbps, 4 : 8.842 kbps (for RFM #1)
    <n>M     bits 1: 17.241 kbps, 2 : 9.579 kbps, 4 : 8.842 kbps (for RFM #2)
    <n>r     use one of the possible data rates (for RFM #1)
    <n>R     use one of the possible data rates (for RFM #2)
    <n>t     0=no toggle, else interval in seconds (for RFM #1)
    <n>T     0=no toggle, else interval in seconds (for RFM #2)
       v     show version
       <n>y     if 1 all received packets will be retransmitted  (Relay mode)
"""

class LaCrosse(object):

    sensors = {}
    _registry = {}
    _callback = None
    _serial = None
    _stopevent = None
    _thread = None

    def __init__(self, port, baud, timeout=2):
        """Initialize the Lacrosse device."""
        self._port = port
        self._baud = baud
        self._timeout = timeout
        self._serial = SerialPortFactory().create_serial_port(port)
        self._callback_data = None

    def open(self):
        """Open the device."""
        self._serial.port = self._port
        self._serial.baudrate = self._baud
        self._serial.timeout = self._timeout
        self._serial.open()
        self._serial.flushInput()
        self._serial.flushOutput()

    def close(self):
        """Close the device."""
        self._stop_worker()
        self._serial.close()

    def start_scan(self):
        """Start scan task in background."""
        self._start_worker()

    def _write_cmd(self, cmd):
        """ensure there is enough time between commands"""
        time.sleep(0.5)
        """Write a cmd."""
        self._serial.write(cmd.encode())


    @staticmethod
    def _parse_info(line):
        """
        The output can be:
        - [LaCrosseITPlusReader.10.1s (RFM12B f:0 r:17241)]
        - [LaCrosseITPlusReader.10.1s (RFM12B f:0 t:10~3)]
        """
        re_info = re.compile(
            r'\[(?P<name>\w+).(?P<ver>.*) ' +
            r'\((?P<rfm1name>\w+) (\w+):(?P<rfm1freq>\d+) ' +
            r'(?P<rfm1mode>.*)\)\]')

        info = {
            'name': None,
            'version': None,
            'rfm1name': None,
            'rfm1frequency': None,
            'rfm1datarate': None,
            'rfm1toggleinterval': None,
            'rfm1togglemask': None,
        }
        match = re_info.match(line)
        if match:
            info['name'] = match.group('name')
            info['version'] = match.group('ver')
            info['rfm1name'] = match.group('rfm1name')
            info['rfm1frequency'] = match.group('rfm1freq')
            values = match.group('rfm1mode').split(':')
            if values[0] == 'r':
                info['rfm1datarate'] = values[1]
            elif values[0] == 't':
                toggle = values[1].split('~')
                info['rfm1toggleinterval'] = toggle[0]
                info['rfm1togglemask'] = toggle[1]

        return info

    def get_info(self):
        """Get current configuration info from 'v' command."""
        re_info = re.compile(r'\[.*\]')

        self._write_cmd('v')
        while True:
            line = self._serial.readline()
            try:
                line = line.encode().decode('utf-8')
            except AttributeError:
                line = line.decode('utf-8')

            match = re_info.match(line)
            if match:
                return self._parse_info(line)

    def led_mode_state(self, state):
        """Set the LED mode.

        The LED state can be True or False.
        """
        self._write_cmd('{}a'.format(int(state)))

    def set_frequency(self, frequency, rfm=1):
        """Set frequency in kHz.

        The frequency can be set in 5kHz steps.
        """
        cmds = {1: 'f', 2: 'F'}
        self._write_cmd('{}{}'.format(frequency, cmds[rfm]))

    def set_datarate(self, rate, rfm=1):
        """Set datarate (baudrate)."""
        cmds = {1: 'r', 2: 'R'}
        self._write_cmd('{}{}'.format(rate, cmds[rfm]))

    def set_toggle_interval(self, interval, rfm=1):
        """Set the toggle interval."""
        cmds = {1: 't', 2: 'T'}
        self._write_cmd('{}{}'.format(interval, cmds[rfm]))

    def set_toggle_mask(self, mode_mask, rfm=1):
        """Set toggle baudrate mask.

        The baudrate mask values are:
          1: 17.241 kbps
          2 : 9.579 kbps
          4 : 8.842 kbps
        These values can be or'ed.
        """
        cmds = {1: 'm', 2: 'M'}
        self._write_cmd('{}{}'.format(mode_mask, cmds[rfm]))

    def _start_worker(self):
        if self._thread is not None:
            return
        self._stopevent = threading.Event()
        self._thread = threading.Thread(target=self._refresh, args=())
        self._thread.daemon = True
        self._thread.start()

    def _stop_worker(self):
        if self._stopevent is not None:
            self._stopevent.set()
        if self._thread is not None:
            self._thread.join()

    def _refresh(self):
        """Background refreshing thread."""

        while not self._stopevent.isSet():
            line = self._serial.readline()
            #this is for python2/python3 compatibility. Is there a better way?
            try:
                line = line.encode().decode('utf-8')
            except AttributeError:
                line = line.decode('utf-8')

            if LaCrosseSensor.re_reading.match(line):
                sensor = LaCrosseSensor(line)
                self.sensors[sensor.sensorid] = sensor

                if self._callback:
                    self._callback(sensor, self._callback_data)

                if sensor.sensorid in self._registry:
                    for cbs in self._registry[sensor.sensorid]:
                        cbs[0](sensor, cbs[1])

    def register_callback(self, sensorid, callback, user_data=None):
        """Register a callback for the specified sensor id."""
        if sensorid not in self._registry:
            self._registry[sensorid] = list()
        self._registry[sensorid].append((callback, user_data))

    def register_all(self, callback, user_data=None):
        """Register a callback for all sensors."""
        self._callback = callback
        self._callback_data = user_data


class LaCrosseSensor(object):
    """The LaCrosse Sensor class."""
    # OK 9 248 1 4 150 106
    re_reading = re.compile(r'OK (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)')

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


class SerialPortFactory(object):
    def create_serial_port(self, port):
        if port.startswith("rfc2217://"):
            from serial.rfc2217 import Serial
            return Serial()
        else:
            from serial import Serial
            return Serial()
