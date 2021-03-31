
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
        self.rejection_block_cnt = 0    # out of receiving window
        self.block_cnt = 0
        self.link_rate_calculation_window = 1.0   # update link rate every 5s
        self.secs_elapsed_since_window_begin = 0.0
        self.ul_secs_elapsed_since_window_begin = 0.0
        self.dl_bytes = 0
        self.ul_bytes = 0
        self.dl_latest_timestamp = None
        self.ul_latest_timestamp = None
        self.start_timestamp = None
        self.timestamps = []
        self.ul_timestamps = []
        self.dl_rates = []
        self.ul_rates = []

    def set_source(self, source):
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
        if self.start_timestamp is None:
            self.start_timestamp = packet.get_timestamp() 

        # CRC error occurs
        if content.find("CRC") != -1:   
            self.error_block_cnt += 1
            self.signals["crc_error"].emit(msg)
            # print("CRC error")

        # packet is rejected because of invalid SN
        if content.find("out of receiving window") != -1 and self.block_cnt > 0:
            self.rejection_block_cnt += 1
            self.signals["rejection"].emit(msg)
            # print("out of receiving window!")

        ret = content.find("RBID = ")
        # this line contains downlink mac information
        if ret != -1:
            # print("dl arrives: ", content)
            self.block_cnt += 1
            self.signals["dl"].emit()
            begin = content.find("BSN")
            end = content.find(",", begin)
            try:
                dl_bsn = int(content[begin + 6:end])
            except:
                pass
            else:
                begin = content.find("PDU length")
                try:
                    pdu_length = int(content[begin + 13:])
                except:
                    pass
                else:
                    self.signals["dl_blk_size"].emit(pdu_length)
                    self.dl_bytes += pdu_length
                    # print("pdu_length: ", pdu_length)
                    # print("dl_bytes: ", self.dl_bytes)
                    current_block_timestamp = packet.get_timestamp()
                    # print("ts:", current_block_timestamp)
                    if self.dl_latest_timestamp is None:
                        self.dl_latest_timestamp = current_block_timestamp
                    else:
                        secs_elapsed = (current_block_timestamp - self.dl_latest_timestamp).total_seconds()
                        # print("secs_elapsed:", secs_elapsed)
                        self.secs_elapsed_since_window_begin += secs_elapsed
                        # print("total_secs:", self.secs_elapsed_since_window_begin)
                        if self.secs_elapsed_since_window_begin > self.link_rate_calculation_window:
                            # recalculate dl rate
                            self.timestamps.append((current_block_timestamp - self.start_timestamp).total_seconds())
                            self.dl_rates.append(self.dl_bytes / self.secs_elapsed_since_window_begin)
                            self.signals["update_dl_rate"].emit({
                                "secs": self.secs_elapsed_since_window_begin,
                                'bytes': self.dl_bytes
                            })
                            # reset
                            self.dl_bytes = 0
                            self.secs_elapsed_since_window_begin = 0
                            self.dl_latest_timestamp = None
            
        ret = content.find('rlc_blk_ptr')
        # this line contains uplink rlc/mac information
        if ret != -1:
            # print("ul arrives: ", content)
            begin = content.find("bsn:")
            new_rlc_bsn = int(content[begin + 4: content.find(' ', begin + 4)])
            begin = content.find("blk_size")
            if begin != -1:
                # print("content=", content)
                pdu_length = int(content[begin + 9: content.find(" ", begin + 9)])
                self.signals["ul_blk_size"].emit(pdu_length)
                print("pdu_length: ", pdu_length)
                self.ul_bytes += pdu_length 
                current_block_timestamp = packet.get_timestamp()
                if self.ul_latest_timestamp is None:
                    self.ul_latest_timestamp = current_block_timestamp
                else:
                    secs_elapsed = (current_block_timestamp - self.ul_latest_timestamp).total_seconds()
                    # print("secs_elapsed:", secs_elapsed)
                    self.ul_secs_elapsed_since_window_begin += secs_elapsed
                    print("total_secs:", self.ul_secs_elapsed_since_window_begin)
                    if self.ul_secs_elapsed_since_window_begin > self.link_rate_calculation_window:
                        # recalculate dl rate
                        self.ul_timestamps.append((current_block_timestamp - self.start_timestamp).total_seconds())
                        self.ul_rates.append(self.ul_bytes / self.ul_secs_elapsed_since_window_begin)
                        self.signals["update_ul_rate"].emit({
                            "secs": self.ul_secs_elapsed_since_window_begin,
                            'bytes': self.ul_bytes
                        })
                        # reset
                        self.ul_bytes = 0
                        self.ul_secs_elapsed_since_window_begin = 0
                        self.ul_latest_timestamp = None