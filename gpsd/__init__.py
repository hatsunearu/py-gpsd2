import socket
import json
import logging

gpsd_socket = None
gpsd_stream = None
state = {}


def _parse_state_packet(json_data):
    global state
    if json_data['class'] == 'DEVICES':
        state['devices'] = json_data
    elif json_data['class'] == 'WATCH':
        state['watch'] = json_data
    else:
        raise Exception("Unexpected message received from gps: {}".format(json_data['class']))


class NoFixError(Exception):
    pass


class GpsResponse(object):
    """ Class representing geo information returned by GPSD """

    def __init__(self):
        self.mode = 0
        self.sats = 0
        self.lon = 0
        self.lat = 0
        self.alt = 0
        self.track = 0
        self.hspeed = 0
        self.climb = 0
        self.error = {}

    @classmethod
    def from_json(cls, packet):
        """ Create GpsResponse instance based on the json data from GPSD
        :type packet: dict
        :param packet: JSON decoded GPSD response
        :return: GpsResponse
        """
        result = cls()
        last_tpv = packet['tpv'][-1]
        last_sky = packet['sky'][-1]

        result.sats = len(last_sky['satellites'])
        result.mode = last_tpv['mode']

        if last_tpv['mode'] >= 2:
            result.lon = last_tpv['lon']
            result.lat = last_tpv['lat']
            result.track = last_tpv['track']
            result.hspeed = last_tpv['speed']
            result.error = {
                'c': 0,
                's': last_tpv['eps'],
                't': last_tpv['ept'],
                'v': 0,
                'x': last_tpv['epx'],
                'y': last_tpv['epy']
            }

        if last_tpv['mode'] >= 3:
            result.alt = last_tpv['alt']
            result.climb = last_tpv['climb']
            result.error['c'] = last_tpv['epc'],
            result.error['v'] = last_tpv['epv']

        return result

    def position(self):
        """ Get the latitude and longtitude as tuple """
        if self.mode < 2:
            raise NoFixError("Needs at least 2D fix")
        return self.lat, self.lon

    def altitude(self):
        """ Get the altitude in meters """
        if self.mode < 3:
            raise NoFixError("Needs at least 3D fix")
        return self.alt

    def movement(self):
        """ Get the speed and direction of the current movement as dict

        The speed is the horisontal speed.
        The climb is the vertical speed
        The track is te direction of the motion
        """
        if self.mode < 3:
            raise NoFixError("Needs at least 3D fix")
        return {"speed": self.hspeed, "track": self.track, "climb": self.climb}

    def speed_vertical(self):
        """ Get the vertical speed with the small movements filtered out. """
        if abs(self.climb) < self.error['c']:
            return 0
        else:
            return self.climb

    def speed(self):
        """ Get the horisontal speed with the small movements filtered out."""
        if self.mode < 2:
            raise NoFixError("Needs at least 2D fix")
        if self.hspeed < self.error['s']:
            return 0
        else:
            return self.hspeed

    def position_precision(self):
        """ Get the error margin in meters for the current fix."""
        if self.mode < 2:
            raise NoFixError("Needs at least 2D fix")
        return max(self.error['x'], self.error['y']), self.error['v']

    def map_url(self):
        """ Get a openstreetmap url for the current position
        :return: str
        """
        if self.mode < 2:
            raise NoFixError("Needs at least 2D fix")
        return "http://www.openstreetmap.org/?mlat={}&mlon={}&zoom=15".format(self.lat, self.lon)

    def __repr__(self):
        modes = {
            0: 'No mode',
            1: 'No fix',
            2: '2D fix',
            3: '3D fix'
        }
        if self.mode < 2:
            return "<GpsResponse {}>".format(modes[self.mode])
        if self.mode == 2:
            return "<GpsResponse 2D Fix {} {}>".format(self.lat, self.lon)
        if self.mode == 3:
            return "<GpsResponse 3D Fix {} {} ({} m)>".format(self.lat, self.lon, self.alt)


def connect(host="127.0.0.1", port=2947):
    """ Connect to a GPSD instance
    :param host: hostname for the GPSD server
    :param port: port for the GPSD server
    """
    global gpsd_socket, gpsd_stream, verbose_output, state
    logging.debug("Connecting to gpsd socket at {}:{}".format(host, port))
    gpsd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gpsd_socket.connect((host, port))
    gpsd_stream = gpsd_socket.makefile(mode="rw")
    logging.debug("Waiting for welcome message")
    welcome_raw = gpsd_stream.readline()
    welcome = json.loads(welcome_raw)
    if welcome['class'] != "VERSION":
        raise Exception("Unexpected data received as welcome. Is the server a gpsd 3 server?")
    logging.debug("Enabling gps")
    gpsd_stream.write('?WATCH={"enable":true}\n')
    gpsd_stream.flush()

    for i in range(0, 2):
        raw = gpsd_stream.readline()
        parsed = json.loads(raw)
        _parse_state_packet(parsed)


def get_current():
    """ Poll gpsd for a new position
    :return: GpsResponse
    """
    global gpsd_stream, verbose_output
    logging.debug("Polling gps")
    gpsd_stream.write("?POLL;\n")
    gpsd_stream.flush()
    raw = gpsd_stream.readline()
    response = json.loads(raw)
    if response['class'] != 'POLL':
        raise Exception("Unexpected message received from gps: {}".format(response['class']))
    return GpsResponse.from_json(response)


def device():
    """ Get information about current gps device
    :return: dict
    """
    global state
    return {
        'path': state['devices']['devices'][0]['path'],
        'speed': state['devices']['devices'][0]['bps'],
        'driver': state['devices']['devices'][0]['driver']
    }
