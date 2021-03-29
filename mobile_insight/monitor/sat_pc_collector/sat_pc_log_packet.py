"""
Parse string from Satellite log
"""

__all__ = ["SatPcLogPacket"]

class SatPcLogPacket():
    def __init__(self, string):
        self.__string = string
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