from ada_protocol import BaseTwistedStep, AdaProtocolHandler
import datetime
import ephem
import requests
import pytz


# this all assumes that your clock is right
# and that you're not hitting the internet through a proxy or something
class NightShift(BaseTwistedStep, AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        super(NightShift, self).__init__(*args, **kwargs)

        self.get_location_info()
        self.init_leds()

    def get_location_info(self):
        ip_info = requests.get("https://freegeoip.net/json/", timeout=3)
        # see how the exception raises later
        geo_json = ip_info.json()
        geo_lat = geo_json.get('latitude')
        geo_lon = geo_json.get('longitude')
        geo_tz = geo_json.get('time_zone')
        now = datetime.datetime.now(pytz.timezone(geo_tz))

        observer = ephem.Observer()
        observer.pressure = 0
        observer.horizon = '-0:34'
        observer.lat = str(geo_lat) # this fucking library
        observer.lon = str(geo_lon)

        rise = observer.previous_rising(ephem.Sun())
        set = observer.next_setting(ephem.Sun())

        observer.horizon = '-18' # astronomical twilight
        twilight_r = observer.previous_rising(ephem.Sun(), use_center=True)
        twilight_s = observer.next_setting(ephem.Sun(), use_center=True)

        # do more things with the time here
        # figure out the offsets from twilight/sunset/etc



    def init_leds(self):
        for led in self.leds:
            led.status = 0