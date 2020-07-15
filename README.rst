Pure Python Jeelink LaCrosse Library
====================================

|BuildStatus| |PypiVersion| |PyPiPythonVersions| |Coveralls| |CodeClimate|


Requirements
------------

This libray works with the `Jeelink`_ USB RF adapter and the arduino `sketch`_ hosted on the `FHEM`_ website.

Tested Devices
--------------
* Technoline TX 29IT
* Technoline TX 29DTH-IT

Command Line Tool
-----------------

.. code :: shell

    # pylacrosse -h
    usage: LaCrosse sensor CLI tool. [-h] [-v] [-d DEVICE] [-f FREQUENCY_RFM1]
                                     [-F FREQUENCY_RFM2] [-t TOGGLE_INTERVAL_RFM1]
                                     [-T TOGGLE_INTERVAL_RFM2]
                                     [-m TOGGLE_MASK_RFM1] [-M TOGGLE_MASK_RFM2]
                                     [-r DATARATE_RFM1] [-R DATARATE_RFM2]
                                     {scan,info,led} ...

    optional arguments:
      -h, --help            show this help message and exit
      -v                    be more verbose
      -d DEVICE, --device DEVICE
                            set local device e.g. '/dev/ttyUSB0' or
                            set remote device e.g. 'rfc2217://[IP]:[PORT]'
                            default: '/dev/ttyUSB0'
      -f FREQUENCY_RFM1     set the frequency for RFM1
      -F FREQUENCY_RFM2     set the frequency for RFM2
      -t TOGGLE_INTERVAL_RFM1
                            set the toggle interval for RFM1
      -T TOGGLE_INTERVAL_RFM2
                            set the toggle interval for RFM2
      -m TOGGLE_MASK_RFM1   set the toggle mask for RFM1
      -M TOGGLE_MASK_RFM2   set the toggle mask for RFM2
      -r DATARATE_RFM1      set the datarate for RFM1
      -R DATARATE_RFM2      set the datarate for RFM2

    Commands:
      {scan,info,led}
        scan                Show all received sensors
        info                Get configuration info
        led                 Set traffic LED state


The LaCrosse sensor generates the ID every time the battery is changed.

Use the cli tool pylacrosse to find your device:

.. code :: shell

    # pylacrosse -d /dev/ttyUSB0 scan
    id=40 t=16.000000 h=69 nbat=0 name=unknown
    id=16 t=18.700000 h=60 nbat=0 name=unknown
    id=0 t=17.400000 h=65 nbat=0 name=unknown

You can generate a file with know devices at ~/.lacrosse/known_sensors.ini

.. code :: shell

    [0]
    name = Kitchen
    [16]
    name = Livingroom
    [40]
    name = Bedroom

then the tool will print the defined names

.. code :: shell

    # pylacrosse -d /dev/ttyUSB0 scan
    id=40 t=16.000000 h=69 nbat=0 name=Bedroom
    id=16 t=18.700000 h=60 nbat=0 name=Livingroom
    id=0 t=17.400000 h=65 nbat=0 name=Kitchen

Using remote serial port with ser2net
-------------------------------------

You can also use ser2net to connect to a remote JeeLink Adapter. This can be useful, if you use
a docker container or if you can not attach a JeeLink adapter to your host running pylacrosse. On your
remote device install ser2net and add the following line to your ser2net.conf:

.. code :: shell

    20001:telnet:0:/dev/ttyUSB0:57600 remctl banner

Restart the ser2net daemon and connect to your remote host using pylacrosse command line tool:

.. code :: shell

    # pylacrosse -d rfc2217://[REMOTE_IP]]:20001 scan
    id=40 t=16.000000 h=69 nbat=0 name=Bedroom
    id=16 t=18.700000 h=60 nbat=0 name=Livingroom
    id=0 t=17.400000 h=65 nbat=0 name=Kitchen

.. _Jeelink: https://www.digitalsmarties.net/products/jeelink
.. _sketch: https://svn.fhem.de/trac/browser/trunk/fhem/contrib/arduino/36_LaCrosse-LaCrosseITPlusReader.zip
.. _FHEM: https://wiki.fhem.de/wiki/JeeLink

.. |BuildStatus| image:: https://travis-ci.org/hthiery/python-lacrosse.png?branch=master
                 :target: https://travis-ci.org/hthiery/python-lacrosse
.. |PyPiVersion| image:: https://badge.fury.io/py/pylacrosse.svg
                 :target: http://badge.fury.io/py/pylacrosse
.. |PyPiPythonVersions| image:: https://img.shields.io/pypi/pyversions/pylacrosse.svg
                        :alt: Python versions
                        :target: http://badge.fury.io/py/pylacrosse
.. |CodeClimate| image:: https://api.codeclimate.com/v1/badges/fc83491ef0ae81080882/maintainability
                 :target: https://codeclimate.com/github/hthiery/python-lacrosse/maintainability
                 :alt: Maintainability
.. |Coveralls|   image:: https://coveralls.io/repos/github/hthiery/python-lacrosse/badge.svg?branch=master
                 :target: https://coveralls.io/github/hthiery/python-lacrosse?branch=master
