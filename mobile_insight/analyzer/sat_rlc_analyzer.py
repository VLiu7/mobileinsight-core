
"""
A Satellite RLC analyzer to get link layer information
"""

from mobile_insight.analyzer.analyzer import *
import datetime
import re
from collections import deque
from enum import Enum

__all__ = ["SatRlcAnalyzer"]

class Ack_state(Enum):
    INIT = 1        # not sent
    SENT = 2        # sent, not acked
    ACKED = 3       # acked
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
        self.last_ul_bsn = None
        self.jumped = True
        self.started = False
        self.pdcp_sn = -1
        self.packet_info = deque()
        self.pdcp_curr = 0
        self.rlc_curr = 0
        self.ul_buffer_delay_secs = []
        self.total_bytes = 0
        self.jump_times = 0
        self.packet_size = 86
        self.packet_acked_info = {} # key: bsn; value: {state: <ACK_STATE>, timestamp: <timestamp>}
        self.propa_delays = []

        self.dl_rlc_curr = 0
        self.dl_pdcp_curr = 0
        self.dl_waiting_for_check = False
        self.dl_temp_block = None
        self.dl_packet_info = deque()
        self.dl_buffer_delay_list = []

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

        # downlink rlc/mac block
        if content.find('RBID') != -1:
            ts = packet.get_timestamp()
            new_dl_bsn = int(re.findall(r'\d+', content[content.find('BSN'):])[0])
            tfi = int(re.findall(r'\d+', content[content.find('TFI'):])[0])
            data_bytes = int(re.findall(r'\d+', content[content.find('PDU length'):])[0])
            self.dl_temp_block = {
                'tfi': tfi,
                'bsn': new_dl_bsn,
                'start': self.dl_rlc_curr,
                'end': self.dl_rlc_curr + data_bytes - 1,
                'entry_timestamp': ts,
                'error': False
            }
            self.dl_waiting_for_check = True

        # out of receiving window
        elif content.find('out of receiving') != -1:
            self.dl_temp_block = None
        elif self.dl_waiting_for_check:
            self.dl_waiting_for_check = False
            if self.dl_temp_block is not None:
                if len(self.dl_packet_info) > 0 and \
                    self.dl_temp_block['bsn'] != (self.dl_packet_info[-1]['bsn'] + 1) % 1024:
                    print('jump')
                self.dl_packet_info.append(self.dl_temp_block)
                self.dl_rlc_curr += (self.dl_temp_block['end'] - self.dl_temp_block['start'] + 1)
                print('add valid block: {}'.format(self.dl_packet_info[-1]))
            self.dl_temp_block = None

        # detect reasembly
        if content.find('reasm peer len') != -1:
            ts = packet.get_timestamp()
            reasm_size = int(re.findall(r'\d+', content[content.find('peer'):])[0])
            first_block = True
            start_ts = None
            bytes_delivered = 0
            total_bytes_delivered = 0
            while len(self.dl_packet_info) > 0:
                oldest_packet = self.dl_packet_info[0]
                if first_block:
                    start_ts = oldest_packet['entry_timestamp']
                    first_block = False
                    bytes_delivered = (oldest_packet['end'] - self.dl_pdcp_curr + 1)
                    packet_delay = (ts - start_ts).total_seconds()
                    print('packet_delay=', packet_delay)
                    self.dl_buffer_delay_list.append({
                        'timestamp': (ts - self.start_timestamp).total_seconds(),
                        'delay': packet_delay
                    })
                    self.signals['dl_buffer_delay'].emit()
                    print('dl_buffer_list:', self.dl_buffer_delay_list[-1])
                else:
                    bytes_delivered = (oldest_packet['end'] - oldest_packet['start'] + 1)
                if total_bytes_delivered + bytes_delivered <= reasm_size:
                    total_bytes_delivered += bytes_delivered
                    self.dl_packet_info.popleft()
                    print('delivered block: {}'.format(oldest_packet))
                else:
                    break
            self.dl_pdcp_curr += reasm_size
            
        
        # Ack
        if content.find('ssn=') != -1:
            ts = packet.get_timestamp()  
            ssn = int(re.findall(r'\d+', content[content.find('ssn='):])[0])
            va = int(re.findall(r'\d+', content[content.find('va='):])[0])
            acked_list = []
            if ssn >= va:
                acked_list = range(va, ssn)
            else:
                acked_list = list(range(va, 1024)) + list(range(0, ssn))
            for bsn in acked_list:
                if self.packet_acked_info.get(bsn) is not None and \
                    self.packet_acked_info[bsn]['state'] == Ack_state.SENT:
                    self.propa_delays.append({
                        'timestamp': (ts - self.start_timestamp).total_seconds(),
                        'delay': (ts - self.packet_acked_info[bsn]['timestamp']).total_seconds()
                    })
                    self.packet_acked_info[bsn] = {
                        'state': Ack_state.ACKED,
                        'timestamp': ts
                    }
                    self.signals['propa_delay'].emit()
                else:
                    print('error! ack not sent')
                    
        # pdcp arrives
        if content.find('pdcp rcv data c') != -1:
            ts = packet.get_timestamp()
            data_bytes = int(re.findall(r'\d+', content[content.find('pdcp rcv'):])[0])
            print('content=', content)
            new_total_bytes = int(re.findall(r'\d+', content[content.find('total'):])[0])
            if self.last_ul_bsn is not None or \
                new_total_bytes == self.total_bytes + data_bytes:
                if self.started:
                    self.pdcp_sn += 1
                    self.packet_info.append({
                        'start': self.pdcp_curr,
                        'end': self.pdcp_curr + data_bytes - 1,
                        'entry_timestamp': ts,
                        'sn': self.pdcp_sn,
                        'queue_size': new_total_bytes
                    })
                    self.pdcp_curr += data_bytes
                self.total_bytes = new_total_bytes
                print(content.strip(), 'sn:', self.pdcp_sn,
                'total_bytes', self.total_bytes,
                'last pdcp packets:', self.packet_info[-1] if self.started else None)
        if content.find('UD bsn') != -1:
            ts = packet.get_timestamp()
            new_ul_bsn = int(re.findall(r'\d+', content[content.find('UD bsn'):])[0])
            jump_detected = False
            new_total_bytes = int(re.findall(r'\d+', content[content.find('total'):])[0])
            data_bytes = self.total_bytes - new_total_bytes
            print('new_bytes=', new_total_bytes, 'total_bytes=', self.total_bytes, 'last_ul_bsn=', self.last_ul_bsn)

            if self.packet_acked_info.get(new_ul_bsn) is None:
                self.packet_acked_info[new_ul_bsn] = {
                    'state': Ack_state.INIT,
                    'timestamp': ts
                }

            if self.packet_acked_info[new_ul_bsn]['state'] == Ack_state.INIT:
                self.packet_acked_info[new_ul_bsn] = {
                    'state': Ack_state.SENT,
                    'timestamp': ts
                }

            elif self.packet_acked_info[new_ul_bsn]['state'] == Ack_state.SENT or Ack_state.ACKED:
                self.packet_acked_info[new_ul_bsn] = {
                    'state': Ack_state.SENT,
                    'timestamp': ts
                }

            # ul queue delay
            if self.last_ul_bsn is not None and new_ul_bsn != (self.last_ul_bsn + 1) % 1024:
                print('sequence jump occurs')
                jump_detected = True
                self.jump_times += 1
            if jump_detected and self.jump_times == 1:
                self.jumped = True
                self.total_bytes = 0
                self.last_ul_bsn = None
            elif jump_detected == False or self.jump_times < 2:
                assert self.last_ul_bsn is None or \
                    (self.total_bytes - new_total_bytes) in [31,30,29] or \
                        self.total_bytes < 31 and new_total_bytes == 0
                # update vars
                self.total_bytes = new_total_bytes
                self.last_ul_bsn = new_ul_bsn
                if self.started:
                    self.rlc_curr += new_total_bytes
                # remove pdcp packets whose all bytes have been sent
                while len(self.packet_info) > 0:
                    oldest_packet = self.packet_info[0]
                    if self.rlc_curr > oldest_packet['end']:
                        self.packet_info.popleft()
                        queue_size_when_entry = oldest_packet['queue_size']
                        delay = (ts - oldest_packet['entry_timestamp']).total_seconds()
                        print('pdcp {} is delivered, pdcp_size = {}, buffer delay = {}, queue_size = {}, rlc_bsn = {}'.format(
                            oldest_packet['sn'],
                            oldest_packet['end'] - oldest_packet['start'] +1 ,
                            delay,
                            queue_size_when_entry,
                            new_ul_bsn
                        ))
                        self.ul_buffer_delay_secs.append({
                            'timestamp': (packet.get_timestamp() - self.start_timestamp).total_seconds(),
                            'delay': delay
                        })
                        self.signals['ul_buffer_delay'].emit()
                    else:
                        break
                if self.total_bytes == 0 and self.jumped and self.started == False:
                    print('start from:', self.last_ul_bsn)
                    self.started = True
                print(content.strip(), 'BSN:', self.last_ul_bsn, 'total_bytes', self.total_bytes, 'rlc_curr:', self.rlc_curr)
        
            self.signals["ul_blk_size"].emit(data_bytes)
            self.ul_bytes += data_bytes 
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
            