
"""
A Satellite RLC analyzer to get link layer information
"""

import re
from mobile_insight.analyzer.analyzer import *

__all__ = ["SatL1Analyzer"]

class SatL1Analyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.log_count = 0
        self.signals = {}

    def set_source(self, source):
        """
        Set the trace source. Enable the cellular signaling messages

        :param source: the trace source (collector).
        """
        Analyzer.set_source(self, source)


    def set_signal(self, name, signal):
        self.signals[name] = signal

    def __msg_callback(self, msg):
        self.log_count += 1
        packet = msg.data
        content = packet.get_content()

        # Find MCS 
        ret = content.find("MCS")
        if ret != -1:
            mcs_value = int(content[ret + 4])
            self.signals["mcs"].emit(mcs_value)

        # Find Signal Strength
        ret = re.findall('-1[0-9]{2} ', content)
        if len(ret) != 0 and content.find('TIM') == -1:
            value = int(ret[0])
            if value > -130 and value < -110:
                self.signals["signal_strength"].emit(int(ret[0]))
