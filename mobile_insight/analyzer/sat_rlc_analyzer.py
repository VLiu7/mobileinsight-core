
"""
A Satellite RLC analyzer to get link layer information
"""

from mobile_insight.analyzer.analyzer import *

__all__ = ["SatRlcAnalyzer"]

class SatRlcAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__msg_callback)
        self.signals = {}
        self.error_block_cnt = 0
        self.block_cnt = 0

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
        packet = msg.data
        # print('packet=', packet)
        # print("type_id=", msg.type_id, ",gps=", packet.get_gps(), ",content=", packet.get_content())
        self.signals["new_log"].emit(msg) 
        content = packet.get_content()

        # CRC error occurs
        if content.find("CRC") != -1:   
            self.signals["crc_error"].emit(msg)
            self.error_block_cnt += 1
            print("CRC error")

        # packet is rejected because of invalid SN
        if content.find("out of receiving window") != -1:
            self.signals["rejection"].emit(msg)
            print("out of receiving window!")

        ret = content.find("RBID = ")
        # this line contains downlink mac information
        if ret != -1:
            self.block_cnt += 1
            begin = content.find("BSN")
            end = content.find(",", begin)
            dl_bsn = int(content[begin + 6:end])
            begin = content.find("PDU length")
            pdu_length = int(content[begin + 13:])
            # dl_bytes.append(dl_bytes[-1] + pdu_length if len(dl_bytes) > 0 else pdu_length)