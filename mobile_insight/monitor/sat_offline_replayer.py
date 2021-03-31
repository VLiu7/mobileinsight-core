"""
An offline log replayer
"""

from .monitor import Monitor, Event
import datetime
import time

__all__ = ["SatOfflineReplayer"]

class SatPcLogPacket():
    def __init__(self, string):
        self.__string = string
        cls = self.__class__
        self.__type_id, self.__timestamp, self.__gps = cls._preparse_internal_list(string)

    def get_type_id(self):
        return self.__type_id

    def get_timestamp(self):
        return self.__timestamp

    def get_gps(self):
        return self.__gps

    def get_content(self):
        return self.__string[56:]

    @classmethod
    def _preparse_internal_list(cls, string):
        if string.find("RLCSEND") != -1 or string.find("SRLC") != -1:
            type_id = "RLC_UL"
        elif string.find("rlc_blk_ptr") != -1:
            type_id = "RLC_UL"
        elif string.find("RLCMAC") != -1 or string.find("RBID") != -1 or string.find("receiving window") != -1:
            type_id = "RLC_DL"
        elif string.find("SMAC") != -1 or string.find("RBID") != -1:
            type_id = "SMAC"
        elif string.find("L1") != -1:
            type_id = "L1"
        else:
            type_id = "None"
        timestamp_str = string[1:string.find("]")]
        try:
            timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        except:
            return None, None, None
        else:
            gps_str = string[len(timestamp_str)+4:string.find("]", len(timestamp_str)+4)]
            # print(gps_str)
            return type_id, timestamp, gps_str

class SatOfflineReplayer(Monitor):
    """
    A log replayer for offline analysis.
    """
    
    def __init__(self):
        Monitor.__init__(self)
        self.log_count = 0

    def set_input_path(self, path):
        self._input_path = path

    def run(self):
        self.__input_file = open(self._input_path, "r")
        start_timestamp = None
        last_timestamp = None
        while True:
            s = self.__input_file.readline()
            if len(s) <= 0:
                break
            packet = SatPcLogPacket(s)
            type_id = packet.get_type_id()
            gps = packet.get_gps()
            timestamp = packet.get_timestamp()
            # print("type_id:", type_id, ",timestamp:", timestamp, ",gps:", gps)
            if timestamp is not None:
                if last_timestamp is not None:
                    gap = (timestamp - last_timestamp).total_seconds()
                else:
                    gap = 0
                last_timestamp = timestamp
                self.log_count += 1
                event = Event(timestamp, type_id, packet)
                self.send(event)
                time.sleep(0.01)
    