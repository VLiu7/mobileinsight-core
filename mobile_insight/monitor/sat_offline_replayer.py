"""
An offline log replayer
"""

from .monitor import Monitor, Event

__all__ = ["SatOfflineReplayer"]

class SatPcLogPacket():
    def __init__(self, string):
        self.__string = string
        cls = self.__class__
        self.__type_id = cls._preparse_internal_list(string)

    def get_type_id(self):
        return self.__type_id

    @classmethod
    def _preparse_internal_list(cls, string):
        if string.find("RLCSEND") != -1 or string.find("SRLC") != -1:
            return "RLC_UL"
        if string.find("rlc_blk_ptr") != -1:
            return "RLC_UL"
        if string.find("RLCMAC") != -1 or string.find("RBID") != -1 or string.find("receiving window") != -1:
            return "RLC_DL"
        if string.find("SMAC") != -1 or string.find("RBID") != -1:
            return "SMAC"
        if string.find("L1") != -1:
            return "L1"
        return "None"

class SatOfflineReplayer(Monitor):
    """
    A log replayer for offline analysis.
    """
    
    def __init__(self):
        Monitor.__init__(self)

    def set_input_path(self, path):
        self._input_path = path

    def run(self):
        self.__input_file = open(self._input_path, "r")
        while True:
            s = self.__input_file.readline()
            if len(s) <= 0:
                break
            packet = SatPcLogPacket(s)
            type_id = packet.get_type_id()
            print("type_id:", type_id)
            # TODO: send to analyzer
    