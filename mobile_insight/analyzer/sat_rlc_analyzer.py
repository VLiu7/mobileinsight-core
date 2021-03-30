
"""
A Satellite RLC analyzer to get link layer information
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["SatRlcAnalyzer"]

class SatRlcAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

    def set_source(self, source):
        #TODO:
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)

    def __msg_callback(self, msg):
        #TODO:
        # print('sat_rlc_analyzer.callback!')
        # print('msg=', msg)
        packet = msg.data
        # print('packet=', packet)
        print("type_id=", msg.type_id, ",gps=", packet.get_gps(), ",content=", packet.get_content())