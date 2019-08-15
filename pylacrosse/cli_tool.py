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


def configure(lacrosse, config, args):
    if args.frequency_rfm1:
        lacrosse.set_frequency(args.frequency_rfm1, 1)
    if args.frequency_rfm2:
        lacrosse.set_frequency(args.frequency_rfm2, 2)

    if args.datarate_rfm1:
        lacrosse.set_datarate(args.datarate_rfm1, 1)
    if args.datarate_rfm2:
        lacrosse.set_datarate(args.datarate_rfm1, 2)

    if args.toggle_mask_rfm1:
        lacrosse.set_toggle_mask(args.toggle_mask_rfm1, 1)
    if args.toggle_mask_rfm2:
        lacrosse.set_toggle_mask(args.toggle_mask_rfm2, 2)

    if args.toggle_interval_rfm1:
        lacrosse.set_toggle_interval(args.toggle_interval_rfm1, 1)
    if args.toggle_interval_rfm2:
        lacrosse.set_toggle_interval(args.toggle_interval_rfm1, 2)


def scan(lacrosse, config, args):
    lacrosse.register_all(scan_callback, user_data=config)
    lacrosse.start_scan()
    while True:
        time.sleep(1)

def get_info(lacrosse, config, args):
    info = lacrosse.get_info()
    print('name:     {}'.format(info['name']))
    print('version:  {}'.format(info['version']))
    if 'rfm1name' in info:
        print('rfm1name: {}'.format(info['rfm1name']))
        print('rfm1frequency: {}'.format(info['rfm1frequency']))
        print('rfm1datarate: {}'.format(info['rfm1datarate']))
        print('rfm1toggleinterval: {}'.format(info['rfm1toggleinterval']))
        print('rfm1togglemask: {}'.format(info['rfm1togglemask']))

def led(lacrosse, config, args):
    state = args.led_state.lower() == 'on'
    lacrosse.led_config(state)

def main(args=None):
    parser = argparse.ArgumentParser('LaCrosse sensor CLI tool.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', action='store_true', dest='verbose',
            help='be more verbose')
    parser.add_argument('-d', '--device', type=str, dest='device',
            help='set local device e.g. \'{0}\' or\n'
                 'set remote device e.g. \'rfc2217://[IP]:[PORT]\'\n'
                 'default: \'{0}\''.format(DEFAULT_DEVICE),
            default=DEFAULT_DEVICE)
    parser.add_argument('-f', type=str, dest='frequency_rfm1',
            help='set the frequency for RFM1')
    parser.add_argument('-F', type=str, dest='frequency_rfm2',
            help='set the frequency for RFM2')
    parser.add_argument('-t', type=str, dest='toggle_interval_rfm1',
            help='set the toggle interval for RFM1')
    parser.add_argument('-T', type=str, dest='toggle_interval_rfm2',
            help='set the toggle interval for RFM2')
    parser.add_argument('-m', type=str, dest='toggle_mask_rfm1',
            help='set the toggle mask for RFM1')
    parser.add_argument('-M', type=str, dest='toggle_mask_rfm2',
            help='set the toggle mask for RFM2')
    parser.add_argument('-r', type=str, dest='datarate_rfm1',
            help='set the datarate for RFM1')
    parser.add_argument('-R', type=str, dest='datarate_rfm2',
            help='set the datarate for RFM2')

    _sub = parser.add_subparsers(title='Commands')

    # list all devices
    subparser = _sub.add_parser('scan',
            help='Show all received sensors')
    subparser.set_defaults(func=scan)

    subparser = _sub.add_parser('info',
            help='Get configuration info')
    subparser.set_defaults(func=get_info)

    subparser = _sub.add_parser('led',
            help='Set traffic LED state')
    subparser.add_argument('led_state', type=str, choices=['on', 'off'],
            metavar="STATE", help='LED state')
    subparser.set_defaults(func=led)

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
        lacrosse = pylacrosse.LaCrosse(args.device, 57600)
        lacrosse.open()
        configure(lacrosse, config, args)
        args.func(lacrosse, config, args)

    finally:
        if lacrosse is not None:
            lacrosse.close()

if __name__ == '__main__':
    main()
