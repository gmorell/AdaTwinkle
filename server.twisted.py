# !/usr/bin/env python
import collections
import cgi
import json
import os
import serial
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
    def __init__(self, counter=None, loop=None, device=DummySerialDevice(), step_time=0.1, current_value="default",
                 avail_progs=None, avail_filters = {}, **kwargs):
        self.current_value = current_value
        self.step_time = step_time
        self.available_progs = avail_progs

        if not counter:
            self.counter = WaitingCounter(5)
        else:
            self.counter = counter

        self.service_avail_filters = avail_filters
        self.service_enabled_filters = collections.OrderedDict()
        # these next 2 lines for testing
        self.service_enabled_filters[uuid.uuid4().hex[0:4].upper()] = ['GRB',self.service_avail_filters['GRB']()]
        self.service_enabled_filters[uuid.uuid4().hex[0:4].upper()] = ['GRB',self.service_avail_filters['GRB']()]

        self.counter.filters = self.service_enabled_filters

        if not loop:
            self.loop = task.LoopingCall(self.counter.step)
            self.loop.start(self.step_time)
        else:
            self.loop = loop

        if not device:
            self.device = device
        else:
            self.device = device

        self.update_filters()

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

    def change_program(self, prog, val):
        self.current_value = val

        # # stop the existing one
        loop_old = self.loop
        loop_old.stop()

        # # setup
        self.program_class = prog['class']
        self.program_args = prog['kwargs']

        self.program_args['device'] = self.device
        self.program_args.update(GLOBAL_KWARGS)

        print self.program_args
        initiated_prog = self.program_class(**self.program_args)

        loop_new = task.LoopingCall(initiated_prog.step)
        loop_new.start(self.step_time)
        self.setLoop(loop_new)
        self.setCntr(initiated_prog)
        self.update_filters()

    def update_filters(self):
        self.counter.filters = [f[1] for f in self.service_enabled_filters.values()]

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


if __name__ == "__main__":
    device = DummySerialDevice()
    # device = serial.Serial(LED_PORT, 115200)

    # ctr = WaitingCounter(5)
    # l = task.LoopingCall(ctr.step)
    # l.start(0.1)
    # reactor.listenTCP(1079, LightFactory(counter=ctr, loop=l, device=device))
    # reactor.run()

application = service.Application('lambent_aether')  # , uid=1, gid=1)
s = LightService(avail_progs=avail_progs, avail_filters=avail_filters)
serviceCollection = service.IServiceCollection(application)
s.setServiceParent(serviceCollection)
internet.TCPServer(8660, s.getLightFactory()).setServiceParent(serviceCollection)
internet.TCPServer(8680, server.Site(s.getLightResource())).setServiceParent(serviceCollection)
