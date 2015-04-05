# !/usr/bin/env python
from twisted.internet import defer
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet import utils

from twisted.protocols import basic

from twisted.web import client

### TODO,
# try this out with the serial debug device
# add the various lighting programs and presets to the array


class WaitingCounter(object):
    def __init__(self, val=0):
        self.counter = val

    def step(self):
        self.counter += 1

    def reset(self):
        self.counter = 0

    def proto_value(self):
        return "Waiting for command for %s seconds" % (self.counter / 10)

class DoubleWaitingCounter(WaitingCounter):
    def step(self):
        self.counter += 10


class FingerProtocol(basic.LineReceiver):
    avail_progs = {
        "default": {"class":WaitingCounter, "kwargs":{}},
        "alt": {"class":DoubleWaitingCounter, "kwargs":{}}
    }
    current_value = "default"
    def change_program(self, prog, val):
        self.current_value = val
        self.current_prog = prog

        ## stop the existing one
        loop_old = self.factory.loop
        loop_old.stop()

        ## setup
        self.program_class = prog['class']
        self.program_args = prog['kwargs']
        # TODO:
        # add the target device to the runner
        # smth program_args['device'] = self.device

        initiated_prog = self.program(**self.program_args)

        loop_new = task.LoopingCall(initiated_prog.step)
        loop_new.start(0.1)
        self.factory.setLoop(loop_new)
        self.factory.setCntr(initiated_prog)

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
                self.change_program(prog, val)
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


class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol

    def __init__(self, counter, loop, **kwargs):
        self.counter = counter
        self.loop = loop

    def getCntr(self):
        return self.counter
        # return defer.succeed(self.users.get(user, None))
        # return utils.getProcessOutput("finger", [user])
        # return client.getPage("http://gmp.io")

    def setCntr(self, cntr):
        self.counter = cntr

    def setLoop(self, loop):
        self.loop = loop


ctr = WaitingCounter(5)
l = task.LoopingCall(ctr.step)
l.start(0.1)
reactor.listenTCP(1079, FingerFactory(counter=ctr, loop=l))
reactor.run()
