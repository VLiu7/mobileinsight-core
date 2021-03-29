
"""
A Satellite RLC analyzer to get link layer information
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["SatRlcAnalyzer"]

class SatRlcAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)

    def set_source(self):
        #TODO:
        pass

    def __msg_callback(self, msg):
        #TODO: