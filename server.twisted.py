# !/usr/bin/env python
import collections
from importlib import import_module
import itertools
import json
import netifaces
import os
import serial
import socket
import sys
import uuid
from twisted.application import internet
from twisted.application import service

from twisted.internet import defer
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet import utils

from twisted.protocols import basic

from twisted.web import client
from twisted.web import resource
from twisted.web import server
from twisted.web import static
import txtemplate
from zeroconf import ServiceInfo, Zeroconf
from devices.ada import AdaDevice

from simpleprogs import WaitingCounter
from helpers import DummySerialDevice

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
        def cb(content):
            request.write(content)
            request.setResponseCode(200)
            request.finish()

        d = template.render(**context)
        d.addCallback(cb)
        return server.NOT_DONE_YET


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


class LightProgramEnabledFilterList(resource.Resource):
    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        status = collections.OrderedDict([[k,v[0]] for k,v in self.service.service_enabled_filters.iteritems()])
        retval = json.dumps({"enabled_filters": status})
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
    def __init__(self, counter=None, loop=None, device = AdaDevice(serial=serial.Serial(LED_PORT, 115200)), step_time=0.1, current_value="default",
                 avail_progs=None, avail_filters = {}, default_filters=[], default_prog=None, discovery_name="", **kwargs):
    # def __init__(self, counter=None, loop=None, device = AdaDevice(serial=DummySerialDevice()), step_time=0.1, current_value="default",
    #              avail_progs=None, avail_filters = {}, default_filters=[], default_prog=None,
    #              discovery_name="", **kwargs):
        self.current_value = current_value
        self.step_time = step_time
        self.available_progs = avail_progs

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
        self.announce(discovery_name)

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

    def bigblender(self, upper, lower, count=64):
        blend = [int(lower + x*(upper-lower)/count) for x in range(count)]
        return blend


    def change_program(self, prog, val):
        self.current_value = val

        # # stop the existing one
        if hasattr(self, "loop"):
            loop_old = self.loop
            loop_old.stop()

        # # setup
        self.program_class = prog['class']
        self.program_args = prog['kwargs']

        self.program_args['device'] = self.device
        self.program_args.update(GLOBAL_KWARGS)

        initiated_prog = self.program_class(**self.program_args)
        # doing it here, prevents that flicker
        initiated_prog.filters = self.get_filters()

        ##
        # # Transitions
        if True and hasattr(self.counter, "leds") and hasattr(initiated_prog, "leds"):
        # if self.transition:

            leds_now = [i.read_rgb() for i in self.counter.leds]
            leds_nowflat = list(itertools.chain(*leds_now))

            leds_l8r = [k.read_rgb() for k in initiated_prog.leds]
            leds_l8rflat = list(itertools.chain(*leds_l8r))

            place_to_hold_stuff =  [list() for i in xrange(64)]

            for j,l in zip(leds_nowflat, leds_l8rflat):
                blendvals = self.bigblender(j,l)
                for v,p in zip(blendvals, place_to_hold_stuff):
                    p.append(v)
            print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';print 'HUE';
            print [i[0:3] for i in place_to_hold_stuff]
            for l in place_to_hold_stuff:
                self.device.write(l)
        loop_new = task.LoopingCall(initiated_prog.step)
        loop_new.start(self.step_time)
        self.setLoop(loop_new)
        self.setCntr(initiated_prog)
        self.update_filters()

    def get_filters(self):
        filters = [f[1] for f in self.service_enabled_filters.values()]
        return filters

    def update_filters(self):
        self.counter.filters = self.get_filters()

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

        se = LightProgramSetter(self)
        r.putChild("set", se)

        ass = static.File('assets')
        r.putChild("assets", ass)

        filt_enabled = LightProgramEnabledFilterList(self)
        r.putChild("filt_en", filt_enabled)

        filt_delete = LightProgramRMFilter(self)
        r.putChild("filt_rm", filt_delete)

        filt_add = LightProgramAddFilter(self)
        r.putChild("filt_add", filt_add)

        return r

    def announce(self, discovery_name):
        self.zeroconf = Zeroconf()

        self.zconfigs = []
        for i in netifaces.interfaces():
            if i.startswith("lo"):
                # remove loopback from announce
                continue
            addrs = netifaces.ifaddresses(i)
            if addrs.keys() == [17]:
                continue
            print addrs
            for a in addrs[netifaces.AF_INET]:
                info_desc = {'path': '/progs/', 'name': discovery_name}
                config = ServiceInfo("_http._tcp.local.",
                               "%s.%s.LambentAether._http._tcp.local." % (socket.gethostname(),i),
                               socket.inet_aton(a['addr']), 8680, 0, 0,
                               info_desc, "lambentaether-autodisc-0.local.")

                self.zeroconf.register_service(config)
                self.zconfigs.append(config)

    def stopService(self):
        for c in self.zconfigs:
            self.zeroconf.unregister_service(c)
        self.zeroconf.close()

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

    except ImportError:
        sys.stderr.write("LAMBENT UNABLE TO LOAD CONFIG FILE, USING DEFAULT\n")

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


s = LightService(
    avail_progs=avail_progs,
    avail_filters=avail_filters,
    default_filters=default_filters,
    default_prog=default_prog,
    discovery_name=discovery_name
)
serviceCollection = service.IServiceCollection(application)
s.setServiceParent(serviceCollection)
internet.TCPServer(8660, s.getLightFactory()).setServiceParent(serviceCollection)
internet.TCPServer(8680, server.Site(s.getLightResource())).setServiceParent(serviceCollection)

