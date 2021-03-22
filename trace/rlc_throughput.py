import datetime
import matplotlib.pyplot as plt


if __name__ == '__main__':
    with open('sandstorm_afternoon/shachen2_ping_ip.txt') as f:
        lines = f.readlines()
        timestamps = []
        pdcp_bsns, pdcp_bytes = [], []
        rlc_bsns, rlc_bytes = [], []
        dl_bsns, dl_bytes = [], []
        for line in lines:
            # add timestamp
            ts_str = line[1:20]
            # print('tr_str=', ts_str)
            try:
                ts_obj = datetime.datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            # print('ts_obj=', ts_obj)
            except:
                pass
            else:
                timestamps.append(ts_obj)

                ret = line.find('UD bsn')
                # this line contains uplink pdcp information
                if ret != -1:
                    new_pdcp_bsn = int(line[ret + 8: line.find(',', ret + 8)])
                    pdcp_bsns.append(new_pdcp_bsn)
                    pdcp_bytes.append(pdcp_bytes[-1] + 31 if len(pdcp_bytes) > 0 else 31)
                else:
                    if len(pdcp_bsns) > 0:
                        pdcp_bsns.append(pdcp_bsns[-1])
                    pdcp_bytes.append(pdcp_bytes[-1] if len(pdcp_bytes) > 0 else 0)

                ret = line.find('rlc_blk_ptr')
                # this line contains uplink rlc/mac information
                if ret != -1:
                    new_rlc_bsn = int(line[26: line.find(' ', 26)])
                    rlc_bsns.append(new_rlc_bsn)
                    rlc_bytes.append(rlc_bytes[-1] + 37 if len(rlc_bytes) > 0 else 37)
                else:
                    if len(rlc_bsns) > 0:
                        rlc_bsns.append(rlc_bsns[-1])
                    rlc_bytes.append(rlc_bytes[-1] if len(rlc_bytes) > 0 else 0)
                # print(dl_bytes[-1])
                ret = line.find("RBID = ")
                # this line contains downlink mac information
                if ret != -1:
                    begin = line.find("BSN")
                    end = line.find(",", begin)
                    dl_bsn = int(line[begin + 6:end])
                    dl_bsns.append(dl_bsn)
                    begin = line.find("PDU length")
                    pdu_length = int(line[begin + 13:])
                    dl_bytes.append(dl_bytes[-1] + pdu_length if len(dl_bytes) > 0 else pdu_length)
                else:
                    if len(dl_bsns) > 0:
                        dl_bsns.append(dl_bsns[-1])
                    dl_bytes.append(dl_bytes[-1] if len(dl_bytes) > 0 else 0)


        start_time = timestamps[0]
        secs_elapsed = [(ele - start_time).total_seconds() for ele in timestamps]

        pdcp_gap = len(timestamps) - len(pdcp_bsns)
        pdcp_bsns = [pdcp_bsns[0] - 1] * pdcp_gap + pdcp_bsns

        rlc_gap = len(timestamps) - len(rlc_bsns)
        rlc_bsns = [rlc_bsns[0] - 1] * rlc_gap + rlc_bsns

        dl_gap = len(timestamps) - len(dl_bsns)
        dl_bsns = [dl_bsns[0] - 1] * dl_gap + dl_bsns
        print(dl_bsns)

        # draw ul and dl sequence number in one diagram
        # plt.xlabel('secs elapsed')
        # plt.ylabel('sequence number')
        # plt.plot(secs_elapsed, pdcp_bsns, label='uplink(pdcp to rlc)')
        # plt.plot(secs_elapsed, rlc_bsns, label='uplink(rlc/mac to L1)')
        # plt.plot(secs_elapsed, dl_bsns, label='downlink mac')
        # plt.legend()
        # plt.rcParams['font.sans-serif'] = ['SimHei']
        # plt.title('上下行序列号随时间变化曲线图')
        # plt.show()

        # draw ul and dl bytesin one diagram
        plt.xlabel('secs elapsed')
        plt.ylabel('#bytes')
        plt.plot(secs_elapsed, rlc_bytes, label='uplink')
        plt.plot(secs_elapsed, dl_bytes, label='downlink')
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.title('上下行传输字节数随时间变化曲线图')
        plt.legend()
        plt.show()
                