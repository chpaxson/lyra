import can, time

# https://stackoverflow.com/questions/57274648/receive-message-on-canbus-always-returns-same-value-with-python-can
def _get_message(msg):
    return msg

class CANableBus(object):
    def __init__(self, channel='COM7', ttyBaudrate=2000000, bitrate=500000):
        self.bus = can.interface.Bus(bustype='slcan', channel=channel, ttyBaudrate=ttyBaudrate, bitrate=bitrate)
        self.buffer = can.BufferedReader()
        self.notifier = can.Notifier(self.bus, [_get_message, self.buffer])
        print("CANableBus initialized")

    def send_message(self, message):
        try:
            self.bus.send(message)
            return True
        except can.CanError:
            print("Message not sent!")
            return False

    def read_input(self, id):
        msg = can.Message(arbitration_id=id,
                          data=[0x00],
                          is_extended_id=False)
        self.send_message(msg)
        return self.buffer.get_message()

    def flush_buffer(self):
        msg = self.buffer.get_message()
        while (msg is not None):
            msg = self.buffer.get_message()

    def cleanup(self):
        self.notifier.stop()
        self.bus.shutdown()
        print("CANableBus shutdown.")