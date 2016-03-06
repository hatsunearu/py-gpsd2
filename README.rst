Python3 GPSD client
===================

This is a library for polling gpsd in Python3

Installation
------------

Install through pip::

    $ pip3 install gpsd-py3

Usage
-----

Just import it and poll the gps. Only a single gpsd server a time is supported::

    import gpsd

    # Connect to the local gpsd
    gpsd.connect()

    # Connect somewhere else
    gpsd.connect(host="127.0.0.1", port=123456)

    # Get gps position
    packet = gpsd.get_current()

    # See the inline docs for GpsResponse for the available data
    print(packet.position())

