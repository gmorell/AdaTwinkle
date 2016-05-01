from ada_protocol import BaseTwistedStep, AdaProtocolHandler
import datetime
import ephem
import requests
import pytz


# this all assumes that your clock is right
# and that you're not hitting the internet through a proxy or something
class NightShift(BaseTwistedStep, AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        # # adjustable arguments

        # how soon before morning twilight we start going amber
        self.pre_twilight_r = kwargs.pop("pre_twlilight_r", 60)
        # how soon after evening twilight do we start going amber
        self.post_twilight_s = kwargs.pop("post_twlilight_s", 360)
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
        # offsets from twilight/sunset/etc configurable via kwargs

        # all the values below will be multiplied by the selected global brightness
        # so it can be "off" when not in use

        # hour before twilisht come from $minimum be it off or just barely lit.
        # $min -> amber %40
        # at twilight should be amber %40
        # at sunrise should be amber %80
        # 1/2 hour after sunrise warmw %40 amber %60
        # full hour after sunrise warmw %100 amber %0
        # 4 hours after sunrise warmww %100 coolw %100
        # 4 hours before sunset warmww %100 coolw %100
        # 2 hours before sunset warmw %100 coolw %50
        # full hour before sunset warmw %100 coolw %0
        # at sunset should be warmw %80 amber %10
        # at twilight should be warmw %60 amber %15
        # four hours after twilight warmw %50 amber %30
        # six hours after twilight warmw %9 amber %30
        # seven hours after twilight warmw %0 amber %0 ($min)



    def init_leds(self):
        for led in self.leds:
            led.status = 0