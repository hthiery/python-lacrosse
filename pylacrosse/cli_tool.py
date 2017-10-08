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

import argparse
import logging
import time

import pylacrosse

_LOGGER = logging.getLogger(__name__)

DEFAULT_DEVICE = '/dev/ttyUSB0'

def test_cb_humidity(sensor):
    print(sensor.humidity)

def test_cb_temperature(sensor):
    print(sensor.temperature)

def main(args=None):
    parser = argparse.ArgumentParser('LaCrosse sensor CLI tool.')
    parser.add_argument('-v', action='store_true', dest='verbose',
            help='be more verbose')
    parser.add_argument('-d', '--device', type=str, dest='device',
            default=DEFAULT_DEVICE)

    args = parser.parse_args(args)

    if args.verbose:
        _LOGGER.setLevel(logging.DEBUG)

    lacrosse = None
    try:
        lacrosse = pylacrosse.LaCrosse(args.device, 56700)
        lacrosse.open()
        lacrosse.register_callback(0, test_cb_humidity)
        lacrosse.register_callback(0, test_cb_temperature)

        while True:
            time.sleep(1)
    finally:
        if lacrosse is not None:
            lacrosse.close()


if __name__ == '__main__':
    main()
