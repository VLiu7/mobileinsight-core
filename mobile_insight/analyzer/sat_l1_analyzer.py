
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
        self.mcs_timestamps = []
        self.signal_timestamps = []
        self.start_timestamp = None
        self.mcs_values = []
        self.signal_values = []

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
        current_timestamp = packet.get_timestamp()
        if self.start_timestamp is None:
            self.start_timestamp = current_timestamp

        # Find MCS 
        ret = content.find("MCS")
        if ret != -1:
            try:
                mcs_value = int(content[ret + 4])
                self.mcs_timestamps.append((current_timestamp - self.start_timestamp).total_seconds())
                self.mcs_values.append(mcs_value)
                self.signals["mcs"].emit(mcs_value)
            except:
                pass

        # Find Signal Strength
        ret = re.findall('-1[0-9]{2} ', content)
        if len(ret) != 0 and content.find('TIM') == -1:
            value = int(ret[0])
            if value > -130 and value < -110:
                self.signal_timestamps.append((current_timestamp - self.start_timestamp).total_seconds())
                sig_strength = int(ret[0])
                self.signal_values.append(sig_strength)
                self.signals["signal_strength"].emit(sig_strength)
