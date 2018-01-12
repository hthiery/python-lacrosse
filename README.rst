Pure Python Jeelink LaCrosse Library
====================================

|BuildStatus| |PypiVersion| |Coveralls| |CodeClimate|



Requirements
------------

This libray works with the `Jeelink`_ USB RF adapter and the arduino `sketch`_ hosted on the `FHEM`_ website.

Tested Devices
-------------
* Technoline TX 29IT
* Technoline TX 29DTH-IT

Command Line Tool
-----------------

The LaCrosse sensor generates the ID every time the battery is changed.

Use the cli tool pylacrosse to find your device:

.. code :: shell

    pylacrosse -d /dev/ttyUSB0 scan
    id=40 t=16.000000 h=69 nbat=0 name=unknown
    id=16 t=18.700000 h=60 nbat=0 name=unknown
    id=0 t=17.400000 h=65 nbat=0 name=unknown

You can generate a file with know devices at ~/.lacrosse/known_devices.ini

.. code :: shell

    [0]
    name = Kitchen
    [16]
    name = Livingroom
    [40]
    name = Bedroom

then the tool will print the defined names

.. code :: shell

    pylacrosse -d /dev/ttyUSB0 scan
    id=40 t=16.000000 h=69 nbat=0 name=Bedroom
    id=16 t=18.700000 h=60 nbat=0 name=Livingroom
    id=0 t=17.400000 h=65 nbat=0 name=Kitchen


.. _Jeelink: https://www.digitalsmarties.net/products/jeelink
.. _sketch: https://svn.fhem.de/trac/browser/trunk/fhem/contrib/arduino/36_LaCrosse-LaCrosseITPlusReader.zip
.. _FHEM: https://fhem.de/commandref.html

.. |BuildStatus| image:: https://travis-ci.org/hthiery/python-lacrosse.png?branch=master
                 :target: https://travis-ci.org/hthiery/python-lacrosse
.. |PyPiVersion| image:: https://badge.fury.io/py/pylacrosse.svg
                 :target: http://badge.fury.io/py/pylacrosse
.. |CodeClimate| image:: https://api.codeclimate.com/v1/badges/fc83491ef0ae81080882/maintainability
				 :target: https://codeclimate.com/github/hthiery/python-lacrosse/maintainability
				 :alt: Maintainability
.. |Coveralls|   image:: https://coveralls.io/repos/github/hthiery/python-lacrosse/badge.svg?branch=master
                 :target: https://coveralls.io/github/hthiery/python-lacrosse?branch=master
