import matplotlib.pyplot as plt

if __name__ == '__main__':
    with open('sandstorm_afternoon/shachen2_ping_ip.txt') as f:
        lines = f.readlines()
        bsns = []
        pdu_lengths = []
        out_of_window = []  # 1 if current bsn is out of receiving window, 0 if not
        bow_bsns = []
        crc_error = []
        for line in lines:
            ret = line.find("RBID")
            if ret != -1:
                begin = line.find("BSN")
                end = line.find(",", begin)
                bsns.append(int(line[begin + 6:end]))
                out_of_window.append(0)
                bow_bsns.append(0)
                crc_error.append(0)
                begin = line.find("PDU length")
                pdu_lengths.append(int(line[begin + 13:]))
            ret = line.find('out of receiving window')
            if ret != -1:
                try:
                    out_of_window[-1] = 1
                except:
                    print('out of receiving window error without preceding dl rlcmac info!')
            ret = line.find('CRC')
            if ret != -1:
                crc_error[-1] = 1
            ret = line.find("bow_bsn")
            if ret != -1:
                end = line.find("-", ret)
                bow = int(line[ret + 10: end])
                bow_bsns[-1] = bow
        print("{0:10.2f}% of downlink packets need retransmission".format(100 * sum(out_of_window) / len(out_of_window)))
                
        NOT_RECEIVED = 0
        WAITING_FOR_RETRANSMISSION = 1
        RECEIVED_NO_ERROR = 2   # block is accepted(in receiving window) and passes CRC check
        RECEIVED_CRC_ERROR = 3  # block is accepted(in receiving window) but fails CRC check

        DUPLICATE = 4
        CRC_RETRANSMISSON = 5

        key1 = 'STATUS'
        key2 = 'RECEIVED_TIMES'

        cycles = [dict()]
        current_cycle = 0       # 1023 block per cycle
        duplicate_cnt = 0       # how many blocks are transmitted meaninglessly
        crc_error_retransmissoin = 0    # how many block are retransmitted due to crc error
        retransmit_cnt = 0      # how many blocks are transmitted because of loss
        retransmit_failed_cnt = 0   
        retranmits_success_cnt = 0
        first_transmit_failed = 0   # how many blocks are rejected in first time
        status_list = []    
        for i in range(len(bsns)):
            bsn = bsns[i]
            rejected = out_of_window[i]
            if bsn // 1023 > current_cycle:
                current_cycle += 1
                cycles.append(dict())
            status = cycles[current_cycle]
            if bsn not in status:
                # print('first packet: {}'.format(bsn))
                status[bsn] = {key1: NOT_RECEIVED, key2: 0}
            status[bsn][key2] += 1
            if out_of_window[i] == 0:   # accepted by receiving window
                if status[bsn][key1] == RECEIVED_NO_ERROR:
                    print('error! Receive a packet which has been received without error:{}'.format(bsn)) # actually, received packets will never be received again
                elif status[bsn][key1] == RECEIVED_CRC_ERROR:
                    print('Receive a packet which has been received but fails CRC check: {}'.format(bsn)) # this will never happen too
                else:
                    if status[bsn][key1] == WAITING_FOR_RETRANSMISSION:
                        retransmit_cnt += 1
                        retranmits_success_cnt += 1
                    if crc_error[i] == 0:
                        status[bsn][key1] = RECEIVED_NO_ERROR
                        status_list.append(RECEIVED_NO_ERROR)
                    else:
                        status[bsn][key1] = RECEIVED_CRC_ERROR
                        status_list.append(RECEIVED_CRC_ERROR)
            else:                       # rejected by receiving window
                if status[bsn][key1] == RECEIVED_NO_ERROR:
                    print('error! Duplicate packet:{}'.format(bsn))
                    duplicate_cnt += 1
                    status_list.append(DUPLICATE)
                elif status[bsn][key1] == RECEIVED_CRC_ERROR:
                    print('Sometime ago, this block is accepted but failed CRC check:{}'.format(bsn))
                    crc_error_retransmissoin += 1
                    status_list.append(CRC_RETRANSMISSON)
                else:
                    if status[bsn][key1] == WAITING_FOR_RETRANSMISSION:
                        retransmit_cnt += 1
                        retransmit_failed_cnt += 1
                    else:
                        assert status[bsn][key1] == NOT_RECEIVED
                        first_transmit_failed += 1
                    status[bsn][key1] = WAITING_FOR_RETRANSMISSION
                    status_list.append(WAITING_FOR_RETRANSMISSION)
        assert len(status_list) == len(bsns)
        print(status_list)
        total_cnt = 0
        waiting_for_transmission = 0
        for status in cycles:
            print('\n'.join('{}:{}'.format(k, v) for k,v in status.items()))
            print('---------------***************------------------')
            for k, v in status.items():
                if v[key1] == WAITING_FOR_RETRANSMISSION:
                    waiting_for_transmission += 1
            total_cnt += len(status)
        print('Out of receiving window rate: {0:10.2f}'.format(100 * sum(out_of_window) / len(out_of_window)))
        print('Duplicate due to crc check error: {0:10.2f}'.format(100 * crc_error_retransmissoin / len(bsns)))
        print('Duplicate due to other reasons: {0:10.2f}'.format(100 * duplicate_cnt / len(bsns)))
        print('Retransmission rate: {0:10.2f}'.format(100 * retransmit_cnt / len(bsns)))
        print('success retransmission:{}'.format(retranmits_success_cnt))
        print('waiting for transmission:{}'.format(waiting_for_transmission))
        print('Retransmission success rate: {}'.format(100 * retranmits_success_cnt / len(bsns)))
        print('Retransmission failed rate: {}'.format(100 * retransmit_failed_cnt / len(bsns)))
        print('Failed to transmit in first time: {0:10.2f}'.format(100 * first_transmit_failed / len(bsns)))

        color_set = [[1,0,0], [0,1,0], [0,0,1], [1,1,0], [1,0,1], [0,1,1]]  # red, green, blue, yellow, pink, cyan
        colors = [color_set[x] for x in status_list]
        print(status_list)
        color_bow = [[0,0,0] if x > 0 else [1,1,1] for x in bow_bsns]
        for i in range(0, len(bsns), 100):
            plt.scatter(range(i, min(len(bsns), i+100)), bsns[i: i+100], c = colors[i: i+100], s = 11)
            plt.scatter(range(i, min(len(bsns), i+100)), bow_bsns[i: i+100], c = color_bow[i: i + 100], s = 4)
            plt.xlabel('#no of messages')
            plt.ylabel('block sequence number')
            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.title('下行序列号随时间变化')
            plt.show()