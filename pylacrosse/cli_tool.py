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
import codecs
import logging
import os
import time
try:
    from ConfigParser import (SafeConfigParser, NoOptionError)
except ImportError:
    from configparser import (SafeConfigParser, NoOptionError)

import pylacrosse

_LOGGER = logging.getLogger(__name__)

DEFAULT_DEVICE = '/dev/ttyUSB0'
def get_known_sensor_name(sensor_id, config):
    try:
        if str(sensor_id) in config.sections():
            name = config.get(str(sensor_id), 'name')
            return name
    except NoOptionError as e:
        return 'unknown'
    except AttributeError:
        return 'unknown'
    return 'unknown'


def scan_callback(sensor, config):
    name = get_known_sensor_name(sensor.sensorid, config)
    print('%s name=%s' % (sensor, name))

def scan(lacrosse, config, args):
    lacrosse.register_all(scan_callback, user_data=config)
    while True:
        time.sleep(1)

def main(args=None):
    parser = argparse.ArgumentParser('LaCrosse sensor CLI tool.')
    parser.add_argument('-v', action='store_true', dest='verbose',
            help='be more verbose')
    parser.add_argument('-d', '--device', type=str, dest='device',
            default=DEFAULT_DEVICE)

    _sub = parser.add_subparsers(title='Commands')

    # list all devices
    subparser = _sub.add_parser('scan',
            help='Show all received sensors')
    subparser.set_defaults(func=scan)

    args = parser.parse_args(args)

    logging.basicConfig()
    if args.verbose:
        _LOGGER.setLevel(logging.DEBUG)

    try:
        config = SafeConfigParser()
        config.readfp(codecs.open(os.path.expanduser(
                '~/.lacrosse/known_sensors.ini'), 'r', 'UTF-8'))
    except IOError:
        config = None

    lacrosse = None
    try:
        lacrosse = pylacrosse.LaCrosse(args.device, 56700)
        lacrosse.open()
        args.func(lacrosse, config, args)

    finally:
        if lacrosse is not None:
            lacrosse.close()

if __name__ == '__main__':
    main()
