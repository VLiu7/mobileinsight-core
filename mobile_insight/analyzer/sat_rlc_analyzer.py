
"""
A Satellite RLC analyzer to get link layer information
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["SatRlcAnalyzer"]

class SatRlcAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.log_count = 0
        self.signals = {}

    def set_source(self, source):
        #TODO:
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)


    def set_signal(self, name, signal):
        self.signals[name] = signal

    def __msg_callback(self, msg):
        # print('sat_rlc_analyzer.callback!')
        # print('msg=', msg)
        self.log_count += 1
        packet = msg.data
        # print('packet=', packet)
        # print("type_id=", msg.type_id, ",gps=", packet.get_gps(), ",content=", packet.get_content())
        self.signals["new_log"].emit(msg) 
        content = packet.get_content()
        if content.find("CRC") != -1:   # CRC error event
            self.signals["crc_error"].emit(msg)
            print("CRC error")
        elif content.find("out of receiving window") != -1:
            self.signals["rejection"].emit(msg)
            print("out of receiving window!")