class BaseDevice(object):

    def read(self):
        """
        Reads from the device
        :return:
        """
        raise NotImplementedError("This device does not supply a read()")

    def write(self):
        """
        Writes to the device
        :return:
        """
        raise NotImplementedError("This device does not supply a write()")

    def die(self):
        """
        Cleans up connections etc...
        :return:
        """
        raise NotImplementedError("This device does not supply a die()")