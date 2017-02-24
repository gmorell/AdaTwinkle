# !/usr/bin/env python
import collections
import itertools
import json
import netifaces
import socket
import sys
import urlparse
import uuid
from copy import deepcopy
from importlib import import_module

import os
import serial
import txtemplate
from autobahn.twisted.wamp import ApplicationRunner, ApplicationSession
from twisted.application import internet
from twisted.application import service
from twisted.internet import protocol
from twisted.internet import task
from twisted.internet.defer import inlineCallbacks, Deferred, returnValue
from twisted.protocols import basic
from twisted.web import resource
from twisted.web import server
from twisted.web import static
from zeroconf import ServiceInfo, Zeroconf

from devices.ada import AdaDevice
from devices.bt_yifang_sh201 import YifangSH201Device
from devices.esp8266ws2812i2s import ESPDevice
from helpers import DummySerialDevice, rgb_triplet_to_html_hex_code
from simpleprogs import WaitingCounter

LED_COUNT = 240
LED_PORT = "/dev/ttyACM0"
LED_DURATION = 600
LED_FADE_TIME = 0.05
LED_FADE_STEPS = 30

GLOBAL_KWARGS = {
    "led_count": LED_COUNT,
    "run_duration": LED_DURATION,
    "fade_time": LED_FADE_TIME,
    "fade_steps": LED_FADE_STEPS,
}

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
# ## TODO,
# try this out with the serial debug device
# add the various lighting programs and presets to the array


from config import avail_progs, avail_filters


class TelnetLightProtocol(basic.LineReceiver):
    avail_progs = avail_progs
    current_value = "default"

    def lineReceived(self, line):
        countah = self.factory.counter
        if line in ["reset", "r", "r:"]:
            countah.reset()
            self.transport.write("Reset currently running counter. \r\n")
            return

        if line == "kill":
            self.transport.loseConnection()
        if "c:" in line:
            self.transport.write("Currently running: %s\r\n" % self.current_value)
        elif "p:" in line:
            val = line.rsplit('p: ')[1]
            prog = self.avail_progs.get(val, None)
            if prog:
                self.factory.change_program(prog, val)
                self.transport.write("Changed to %s.\r\n" % val)
            else:
                self.transport.write("No Such Prog")

        elif "d:" in line:
            val = line.rsplit('d: ')[1]
            # todo
            # self.device = somewayofgettingthedevice
            # self.change_program(self.current_prog, self.current_val)


        else:
            self.transport.write(str(countah.proto_value()) + "\r\n")
            # return usr.counter
            # def onError(err):
            # return "error"
            #
            # usr.addErrback(onError)
            #
            # def writeAResp(msg):
            # self.transport.write(msg + "\r\n")
            # self.transport.loseConnection()
            #
            # usr.addCallback(writeAResp)


class LightFactory(protocol.ServerFactory):
    protocol = TelnetLightProtocol

    def __init__(self, counter, loop, device, **kwargs):
        self.counter = counter
        self.loop = loop
        self.device = device

    def getCntr(self):
        return self.counter
        # return defer.succeed(self.users.get(user, None))
        # return utils.getProcessOutput("finger", [user])
        # return client.getPage("http://gmp.io")

    def setCntr(self, cntr):
        self.counter = cntr

    def setLoop(self, loop):
        self.loop = loop


class LightHTMLTree(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.loader = txtemplate.Jinja2TemplateLoader(TEMPLATE_DIR)

        self.service = service

    def render_GET(self, request):
        template_name = "landing.jinja2"
        template = self.loader.load(template_name)

        context = {}
        # get data

        progs = self.service.available_progs.keys()
        context['progs'] = progs

        progs_grp = {}
        for k,v in self.service.available_progs.iteritems():
            key = deepcopy(k)
            val = v  # deep copy these so we don't barn the existing things
            grp = v.get("grouping", "NONE")
            if grp in progs_grp:
                progs_grp[grp].append(key)
            else:
                progs_grp[grp] = [key]

        context['progs_grp'] = progs_grp

        def cb(content):
            request.write(content)
            request.setResponseCode(200)
            request.finish()

        d = template.render(**context)
        d.addCallback(cb)
        return server.NOT_DONE_YET

class LightSpeedFaster(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        speed, changed = self.service.loop_faster()
        retval = json.dumps({"current": speed, "changed":changed})
        return retval

class LightSpeedSlower(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        speed, changed = self.service.loop_slower()
        retval = json.dumps({"current": speed, "changed":changed})
        return retval

class LightSpeedOptions(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        speeds = self.service.step_sizes
        current = self.service.step_time
        retval = json.dumps({"avail": speeds, "current":current})
        return retval

class LightSpeedSet(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        val = request.args.get('val', [0.5])[0]
        floaty = float(val)
        if floaty in self.service.step_sizes:
            index = self.service.step_sizes.index(floaty)
            self.service.set_time_index(index)
            return json.dumps(
                {
                    "status": "SPEED_UPDATED",
                    "value": val
                }
            )
        else:
            return json.dumps(
                {
                    "status": "ERROR_INVALID_SPEED_VALUE",
                    "value": val
                }
            )

class LightStatus(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        status = self.service.current_value
        retval = json.dumps({"running": status})
        return retval


class LightProgramSetter(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def handle_get_post(self, prog):
        if prog:
            val = prog[0]
            if val not in self.service.available_progs.keys():
                return json.dumps(
                    {
                        "status": "ERROR_NON_EXISTENT_PROGRAM_PARAMETER",
                        "value": val
                    }
                )
            else:
                prog = self.service.available_progs.get(val, None)
                self.service.change_program(prog, val)
                return json.dumps(
                    {
                        "status": "SUCCESS_CHANGED_PROGRAM",
                        "value": val
                    }
                )
        return json.dumps(
            {
                "status": "ERROR_MISSING_PROGRAM_PARAMETER",
                "value": "prog"
            }
        )

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        prog = request.args.get('prog', None)
        return self.handle_get_post(prog)

    def render_POST(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        prog = request.args.get('prog', None)
        return self.handle_get_post(prog)


class LightProgramList(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        status = sorted(self.service.available_progs.keys())
        retval = json.dumps({"available_progs": status})
        return retval

class LightProgramListGrouped(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        grpd = {}
        for k,v in self.service.available_progs.iteritems():
            key = deepcopy(k)
            val = deepcopy(v) # deep copy these so we don't barn the existing things
            grouping_val = val.get('grouping')
            colors = val.get('colors')
            if not colors:
                ss = val['kwargs'].get('state_storage')
                if not ss:
                    colors = ['#060606']
                    val['colors'] = colors
                else:
                    # set the kwargs
                    ss_kwargs = val['kwargs']
                    del ss_kwargs['state_storage']
                    ss_kwargs['id'] = 1

                    init = ss(**ss_kwargs)
                    colors = []
                    for i in xrange(60):
                        init.do_step()
                        rgb = init.read_rgb()
                        rgb_as_hex = rgb_triplet_to_html_hex_code(rgb)
                        colors.append(rgb_as_hex)
                    val['colors'] = list(set(colors))

            data = {"action":key, "display":val['display'], "color":colors}
            if grouping_val and grouping_val in grpd:
                grpd[grouping_val].append(data)
            elif grouping_val:
                grpd[grouping_val] = [data]

        status = sorted(self.service.available_progs.keys())
        retval = json.dumps({"available_grouped": grpd})
        return retval


class LightProgramEnabledFilterList(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        status = collections.OrderedDict([[k,v[0]] for k,v in self.service.service_enabled_filters.iteritems()])
        retval = json.dumps({"enabled_filters": status})
        return retval


class LightProgramFilterList(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        print self.service.service_avail_filters
        status = collections.OrderedDict([[k,v._desc] for k,v in self.service.service_avail_filters.iteritems()])
        retval = json.dumps({"available_filters": status})
        return retval


class LightProgramRMFilter(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def handle_get_post(self, filt):
        if filt:
            val = filt[0]
            if val not in self.service.service_enabled_filters.keys():
                return json.dumps(
                    {
                        "status": "ERROR_NON_EXISTENT_ENABLED_FILTER_KEY",
                        "value": val
                    }
                )
            else:
                filt = self.service.service_enabled_filters.pop(val)
                self.service.update_filters()
                return json.dumps(
                    {
                        "status": "SUCCESS_REMOVED_FILTER",
                        "value": val
                    }
                )

        return json.dumps(
            {
                "status": "ERROR_MISSING_PARAMETER",
                "value": "filt"
            }
        )

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        filt = request.args.get('filt', None)
        return self.handle_get_post(filt)

    def render_POST(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        filt = request.args.get('filt', None)
        return self.handle_get_post(filt)


class LightProgramAddFilter(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def handle_get_post(self, filt):
        if filt:
            val = filt[0]
            if val not in self.service.service_avail_filters.keys():
                return json.dumps(
                    {
                        "status": "ERROR_NON_EXISTENT_FILTER_KEY",
                        "value": val
                    }
                )
            else:
                self.service.service_enabled_filters[uuid.uuid4().hex[0:4].upper()] = [val,self.service.service_avail_filters[val]()]
                self.service.update_filters()
                return json.dumps(
                    {
                        "status": "SUCCESS_ADDED_FILTER",
                        "value": val
                    }
                )

        return json.dumps(
            {
                "status": "ERROR_MISSING_PARAMETER",
                "value": "filt"
            }
        )

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        filt = request.args.get('filt', None)
        return self.handle_get_post(filt)

    def render_POST(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        filt = request.args.get('filt', None)
        return self.handle_get_post(filt)

class LightService(service.Service):
    step_sizes = [0.01, 0.05, 0.1, 0.5, 1, 5, 10, 30, 60]

    def __init__(self, counter=None, loop=None, device = AdaDevice(serial=DummySerialDevice()), step_time_index=2, current_value="default",
                 avail_progs=None, avail_filters = {}, default_filters=[], default_prog=None, lambent_port=8680,
                 discovery_name="", remote_device_managed=False, xbar_component=None, xbar_runner_kwargs=None, **kwargs):
        self.current_value = current_value
        self.step_time_index = step_time_index
        self.available_progs = avail_progs
        self.remote_device_managed = remote_device_managed

        if not device:
            self.device = device
        else:
            self.device = device

        if default_prog:
            if default_prog in self.available_progs.keys():
                prog = self.available_progs.get(default_prog)
                # self.change_program(prog, default_prog)
                prog_kwargs = prog['kwargs']
                prog_kwargs['device'] = self.device
                prog_kwargs.update(GLOBAL_KWARGS)
                counter = prog['class'](**prog_kwargs)
                self.current_value = default_prog
            else:
                sys.stderr.write("SELECTED (%s) NOT IN (%s)" % (default_prog, ",".join(i for i in self.available_progs)))

        if not counter:
            self.counter = WaitingCounter(5)
        else:
            self.counter = counter

        self.service_avail_filters = avail_filters
        self.service_enabled_filters = collections.OrderedDict()
        for filter in default_filters:
            try:
                self.service_enabled_filters[uuid.uuid4().hex[0:4].upper()] = [filter,self.service_avail_filters[filter]()]
            except:
                sys.stderr.write("LAMBENT FILTER DIDN'T EXIST '" + filter + "', SKIPPING\n")

        # these next 2 lines for testing
        # self.service_enabled_filters[uuid.uuid4().hex[0:4].upper()] = ['GRB',self.service_avail_filters['GRB']()]
        # self.service_enabled_filters[uuid.uuid4().hex[0:4].upper()] = ['GRB',self.service_avail_filters['GRB']()]

        self.counter.filters = self.get_filters()

        if not loop:
            self.loop = task.LoopingCall(self.counter.step)
            self.loop.start(self.step_time)
        else:
            self.loop = loop


        self.update_filters()
        self.disc_name = discovery_name
        self.announce(discovery_name, port=lambent_port)

        if xbar_runner_kwargs:
            self.xbar_session = None
            self.xbar_component = xbar_component
            self.xbar_runner_kwargs = xbar_runner_kwargs
            self.xbar_init()


    @inlineCallbacks
    def _init_xbar(self):
        if self.xbar_session is None:
            self.xbar_session = yield self.start_crossbar()

    @inlineCallbacks
    def start_crossbar(self):
        running_deferred = Deferred()
        extra = dict(running=running_deferred)
        self.xbar_runner_kwargs['extra'] = extra

        xbar_runner = ApplicationRunner(**self.xbar_runner_kwargs)
        xbar_runner.run(self.xbar_component, start_reactor=False, auto_reconnect=True)
        session = yield running_deferred
        returnValue(session)

    # @inlineCallbacks
    def xbar_change_program(self, program):
        # this should be improved and normalized later to not repat code but for now it works
        if program not in self.available_progs.keys():
            return json.dumps(
                    {
                        "status": "ERROR_NON_EXISTENT_PROGRAM_PARAMETER",
                        "value": program
                    }
                )
        else:
            prog = self.available_progs.get(program, None)
            self.change_program(prog, program)
            return json.dumps(
                {
                    "status": "SUCCESS_CHANGED_PROGRAM",
                    "value": program
                }
            )

    @inlineCallbacks
    def xbar_init(self):
        yield self._init_xbar()
        yield self.xbar_hello()
        yield self.xbar_register_methods()

    @inlineCallbacks
    def xbar_register_methods(self):
        xbar_method = "us.thingcosm.aethers.lambent.%(name)s.program" % {"name":self.disc_name.lower()}
        print("qqq")
        print(xbar_method)
        yield self.xbar_session.register(self.xbar_change_program, xbar_method)

    @inlineCallbacks
    def xbar_hello(self):
        yield self.xbar_session.publish("us.thingcosm.aethers.lambent.updates.program", server_name=self.disc_name, server_program=self.current_value)

    @inlineCallbacks
    def xbar_update_speed(self):
        yield self.xbar_session.publish("us.thingcosm.aethers.lambent.updates.speed", server_name=self.disc_name,
                                        server_value=self.step_time)

    @property
    def step_time(self):
        return self.step_sizes[self.step_time_index]

    def getCntr(self):
        return self.counter

    def setCntr(self, cntr):
        self.counter = cntr

    def setLoop(self, loop):
        self.loop = loop

    def setLoopInterval(self, value):
        self.step_time = value
        self.loop.stop()
        self.loop.start(self.step_time)

    # blendy bits
    def bigblender(self, upper, lower, count=64):
        blend = [int(lower + x*(upper-lower)/count) for x in range(count)]
        return blend

    def do_all_filters(self, value):
        for f in self.get_filters():
            value = f.do_filter(value)

        return value

    def change_program(self, prog, val):
        self.current_value = val

        # # stop the existing one
        if hasattr(self, "loop"):
            loop_old = self.loop
            try:
                loop_old.stop()
            except AssertionError:
                pass
                print "too quick slick"


        # # setup
        self.program_class = prog['class']
        self.program_args = prog.get('kwargs', {})
        self.program_args['device'] = self.device
        self.program_args.update(GLOBAL_KWARGS)

        initiated_prog = self.program_class(**self.program_args)
        # doing it here, prevents that flicker
        initiated_prog.filters = self.get_filters()

        ##
        # # Transitions
        if self.counter and hasattr(self.counter, "leds") and hasattr(initiated_prog, "leds"):
        # if self.transition:
            if self.counter.transitions_list:
                leds_nowflat = self.counter.transitions_list.pop(0)
            else:
                leds_now = [i.read_rgb() for i in self.counter.leds]
                leds_filtered = [self.do_all_filters(i) for i in leds_now]
                leds_nowflat = list(itertools.chain(*leds_filtered))


            leds_l8r = [k.read_rgb() for k in initiated_prog.leds]
            leds_l8r_filt = [self.do_all_filters(i) for i in leds_l8r]
            leds_l8rflat = list(itertools.chain(*leds_l8r_filt))

            place_to_hold_stuff =  [list() for i in xrange(128)]

            for j,l in zip(leds_nowflat, leds_l8rflat):
                blendvals = self.bigblender(l,j,count=128)
                for v,p in zip(blendvals, place_to_hold_stuff):
                    p.append(v)

            # for l in place_to_hold_stuff:
            #     self.device.write(l)
        else:
            place_to_hold_stuff = []

        if place_to_hold_stuff and remote_device_managed != False:
            """
            This is a stupid quick implementation of taking far fewer steps,
            its not particularly perfect, but its Good Enough
            """
            len_pl = len(place_to_hold_stuff)

            if remote_device_managed == 0: # no fade
                place_to_hold_stuff = []

            elif remote_device_managed == 1: # half as many
                place_to_hold_stuff = place_to_hold_stuff[::2]

            elif remote_device_managed == 2: # 1/4 as many
                last = place_to_hold_stuff[-1]
                place_to_hold_stuff = place_to_hold_stuff[::4]
                if place_to_hold_stuff[-1] != last:
                    place_to_hold_stuff.append(last)

            elif remote_device_managed == 3:
                last = place_to_hold_stuff[-1]
                place_to_hold_stuff = place_to_hold_stuff[::10]
                if place_to_hold_stuff[-1] != last:
                    place_to_hold_stuff.append(last)

            elif remote_device_managed == 4:
                pass

            elif remote_device_managed == 5 and len_pl > 3: # single intermediate
                start = place_to_hold_stuff[0]
                end = place_to_hold_stuff[-1]
                middle = len_pl/2

                place_to_hold_stuff=[start, place_to_hold_stuff[middle], end]

            elif remote_device_managed == 6 and len_pl > 5:
                start = place_to_hold_stuff[0]
                end = place_to_hold_stuff[-1]
                mid_1 = len_pl / 4 * 1  # 25%ish
                mid_2 = len_pl / 4 * 2  # 50%ish
                mid_3 = len_pl / 4 * 3  # 75%ish

                place_to_hold_stuff = [start, place_to_hold_stuff[mid_1], place_to_hold_stuff[mid_2],
                                       place_to_hold_stuff[mid_3], end]

            elif remote_device_managed == 7 and len_pl > 7:
                start = place_to_hold_stuff[0]
                end = place_to_hold_stuff[-1]
                mid_1 = len_pl / 6 * 1  # 16%ish
                mid_2 = len_pl / 6 * 2  # 32%ish
                mid_3 = len_pl / 6 * 3  # 48%ish
                mid_4 = len_pl / 6 * 4  # 64%ish
                mid_5 = len_pl / 6 * 5  # 80%ish
                place_to_hold_stuff = [start, place_to_hold_stuff[mid_1], place_to_hold_stuff[mid_2],
                                       place_to_hold_stuff[mid_3], place_to_hold_stuff[mid_4],
                                       place_to_hold_stuff[mid_5], end]

            else: # fallback
                place_to_hold_stuff = []
            pass

        initiated_prog.transitions_list = place_to_hold_stuff
        loop_new = task.LoopingCall(initiated_prog.step)
        loop_new.start(self.step_time)
        self.setLoop(loop_new)
        self.setCntr(initiated_prog)
        self.update_filters()
        self.xbar_hello()

    def get_filters(self):
        filters = [f[1] for f in self.service_enabled_filters.values()]
        return filters

    def update_filters(self):
        self.counter.filters = self.get_filters()

    def loop_set(self):
        self.loop.stop()
        self.loop.start(self.step_time)
        self.xbar_update_speed()

    def loop_slower(self):
        max_index = len(self.step_sizes) - 1
        if self.step_time_index >= max_index:
            return self.step_time, False
        else:
            self.step_time_index += 1
            self.loop_set()
            return self.step_time, True
        # return 0,True

    def loop_faster(self):
        if self.step_time_index <= 0:
            return self.step_time, False
        else:
            self.step_time_index -= 1
            self.loop_set()
            return self.step_time, True

    def set_time_index(self, value):
        self.step_time_index = value
        self.loop_set()

    def getLightFactory(self):
        f = protocol.ServerFactory()
        f.protocol = TelnetLightProtocol
        f.counter = self.counter
        f.loop = self.loop
        f.device = self.device

        f.setLoop = self.setLoop
        f.setCntr = self.setCntr
        f.change_program = self.change_program
        return f

    def getLightResource(self):
        r = LightHTMLTree(self)
        r.putChild("", r)

        st = LightStatus(self)
        r.putChild("status", st)

        pl = LightProgramList(self)
        r.putChild("progs", pl)

        plg = LightProgramListGrouped(self)
        r.putChild("progs_grp", plg)

        se = LightProgramSetter(self)
        r.putChild("set", se)

        ass = static.File('assets')
        r.putChild("assets", ass)

        filt_enabled = LightProgramEnabledFilterList(self)
        r.putChild("filt_en", filt_enabled)

        filt_list = LightProgramFilterList(self)
        r.putChild("filt_ls", filt_list)

        filt_delete = LightProgramRMFilter(self)
        r.putChild("filt_rm", filt_delete)

        filt_add = LightProgramAddFilter(self)
        r.putChild("filt_add", filt_add)

        sp_faster = LightSpeedFaster(self)
        r.putChild("sp_up", sp_faster)

        sp_slower = LightSpeedSlower(self)
        r.putChild("sp_dn", sp_slower)

        sp_list = LightSpeedOptions(self)
        r.putChild("sp_ls", sp_list)

        sp_set = LightSpeedSet(self)
        r.putChild("sp_set", sp_set)

        return r

    def announce(self, discovery_name, port=8680):
        self.zeroconf = Zeroconf()

        self.zconfigs = []
        for i in netifaces.interfaces():
            if i.startswith("lo"):
                # remove loopback from announce
                continue
            if i.startswith("veth"):
                # remove docker interface from announce
                continue

            addrs = netifaces.ifaddresses(i)
            if addrs.keys() == [17]:
                continue
            print addrs
            for a in addrs[netifaces.AF_INET]:
                print a
                info_desc = {'path': '/progs_grp/', 'name': discovery_name, "port":port}
                config = ServiceInfo("_aether._tcp.local.",
                               "%s_%s_%s_lambent._aether._tcp.local." % (socket.gethostname(),i, port),
                               socket.inet_aton(a['addr']), port, 0, 0,
                               info_desc)
                try:
                    self.zeroconf.register_service(config)
                    self.zconfigs.append(config)
                except:
                    print("Service %s failed to register" % config)

    def stopService(self):
        for c in self.zconfigs:
            self.zeroconf.unregister_service(c)
        self.zeroconf.close()

class LambentCrossbarComponent(ApplicationSession):
    def __init__(self, config=None):
        ApplicationSession.__init__(self, config)
        print("component created")

    def onConnect(self):
        print("transport connected")
        self.join(self.config.realm)

    def onChallenge(self, challenge):
        print("authentication challenge received")

    def onJoin(self, details):
        self.config.extra['running'].callback(self)
        print("session joined")

    def onDisconnect(self):
        print("transport disconnected")

if __name__ == "__main__":
    device = DummySerialDevice()
    # device = serial.Serial(LED_PORT, 115200)

    # ctr = WaitingCounter(5)
    # l = task.LoopingCall(ctr.step)
    # l.start(0.1)
    # reactor.listenTCP(1079, LightFactory(counter=ctr, loop=l, device=device))
    # reactor.run()

application = service.Application('lambent_aether')  # , uid=1, gid=1)
# lets read the room
if os.environ.has_key("LAMBENTCONFIG"):
    conf_path = os.environ.get("LAMBENTCONFIG")
    try:
        config = import_module(conf_path)
        if hasattr(config, "avail_filters"):
            avail_filters = config.avail_filters
        else:
            sys.stderr.write("LAMBENT CONFIG HAS NO FILTERS, USING DEFAULT\n")
        if hasattr(config, "avail_progs"):
            avail_progs = config.avail_progs
        else:
            sys.stderr.write("LAMBENT CONFIG HAS NO PROGS, USING DEFAULT\n")

        if hasattr(config, "remote_device_managed"):
            """
            Remote devices (like certain superchina bluetooth bulbs) may somewhat manage their fade,
            making the really fancy default fade seem pointless and take forever (like when bulbs chg every 30s)

            Configuration Values :
            False: Full fade
            0: No Fade
            1: 50% as many steps
            2: 25% as many steps
            3: 10% as many steps
            4: 5% as many steps # not implemented yet
            5: 1 Intermediate
            6: 3 Intermediate
            7: 5 Intermediate
            """
            remote_device_managed = config.remote_device_managed
        else:
            remote_device_managed = False

    except ImportError:
        remote_device_managed = False
        sys.stderr.write("LAMBENT UNABLE TO LOAD CONFIG FILE, USING DEFAULT\n")

else:
    remote_device_managed = False

if os.environ.has_key("LAMBENTDEFAULTFILTERS"):
    default_filters = os.environ.get("LAMBENTDEFAULTFILTERS").split(',')
else:
    default_filters = []

if os.environ.has_key("LAMBENTDEFAULTPROGS"):
    default_prog = os.environ.get("LAMBENTDEFAULTPROGS")
else:
    default_prog = None
    sys.stderr.write("NO DEFAULT")

if os.environ.has_key("LAMBENTDISCOVERYNAME"):
    discovery_name = os.environ.get("LAMBENTDISCOVERYNAME")
else:
    discovery_name = "LAMBENT"
    sys.stderr.write("NO NAME SET, USING LAMBENT")

if os.environ.has_key("LAMBENTCROSSBAR"):
    running_deferred = Deferred()
    extra = dict(running=running_deferred)
    crossbar_url = unicode(os.environ.get("LAMBENTCROSSBAR", u"ws://127.0.0.1/ws"))
    crossbar_realm = unicode(os.environ.get("LAMBENTCROSSBARREALM", u"realm1"))
    crossbar_runner_kwargs = {"url": crossbar_url, "realm": crossbar_realm}
    # crossbar_runner = ApplicationRunner(url=crossbar_url, realm=crossbar_realm, extra=extra)
    crossbar_component = LambentCrossbarComponent
    # start(crossbar_runner, crossbar_component)

else:
    crossbar_runner = None
    crossbar_component = None

if os.environ.has_key("LAMBENTSPEEDINDEX"):
    speed_index = int(os.environ.get("LAMBENTSPEEDINDEX", 2))
else:
    speed_index = 2

lambent_port = int(os.environ.get("LAMBENTPORT", 8680))

if lambent_port == 8680:
    sys.stderr.write("USING DEFAULT PORT")

# figure out the connection string
lambent_connect = os.environ.get("LAMBENTCONNECT", "adlserial:///dev/ttyACM0")
print lambent_connect, lambent_port
print type(lambent_port)

# "espudp://192.168.1.1:192.168.1.2"
# "adlserial:///dev/ttyACM0"
# "debug://"
# "btnexturn://C4:ED:BA:56:8D:01::C4:ED:BA:56:8D:02"
parsed = urlparse.urlparse(lambent_connect)
if parsed.scheme == "espudp":
    device_class = ESPDevice
    device_kwargs = {"addrs": parsed.netloc.split(':')}

elif parsed.scheme == "adlserial":
    device_class = AdaDevice
    device_kwargs = {"serial": serial.Serial(parsed.path, 115200)}

elif parsed.scheme == "debug":
    device_class = AdaDevice
    device_kwargs = {"serial": DummySerialDevice()}

elif parsed.scheme == "btnexturn":
    device_class = YifangSH201Device
    device_kwargs = {"devices": parsed.netloc.split('::')}

device = device_class(**device_kwargs)

s = LightService(
    avail_progs=avail_progs,
    avail_filters=avail_filters,
    default_filters=default_filters,
    default_prog=default_prog,
    discovery_name=discovery_name,
    device=device,
    lambent_port=lambent_port,
    step_time_index=speed_index,
    remote_device_managed=remote_device_managed,
    xbar_component=crossbar_component,
    xbar_runner_kwargs=crossbar_runner_kwargs,
)

# if crossbar_component: # this is a totally legit move here
#     s.xbar = crossbar_session
    # crossbar_component.service = s
    # annc = "us.thingcosm.aethers.lambent.updates"


serviceCollection = service.IServiceCollection(application)
s.setServiceParent(serviceCollection)
# internet.TCPServer(8660, s.getLightFactory()).setServiceParent(serviceCollection)
internet.TCPServer(lambent_port, server.Site(s.getLightResource())).setServiceParent(serviceCollection)