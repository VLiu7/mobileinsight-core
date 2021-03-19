import datetime
import matplotlib.pyplot as plt


if __name__ == '__main__':
    with open('shachen2_ping_ip_rlc.txt') as f:
        lines = f.readlines()
        timestamps = []
        ul_bsns, ul_bytes = [], []
        dl_bsns, dl_bytes = [], []
        for line in lines:
            # add timestamp
            ts_str = line[1:20]
            # print('tr_str=', ts_str)
            ts_obj = datetime.datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            # print('ts_obj=', ts_obj)
            timestamps.append(ts_obj)

            ret = line.find('UD bsn')
            # this line contains uplink information
            if ret != -1:
                new_ul_bsn = int(line[ret + 8: line.find(',', ret + 8)])
                ul_bsns.append(new_ul_bsn)
                ul_bytes.append(ul_bytes[-1] + 31 if len(ul_bytes) > 0 else 31)
            else:
                if len(ul_bsns) > 0:
                    ul_bsns.append(ul_bsns[-1])
                ul_bytes.append(ul_bytes[-1] if len(ul_bytes) > 0 else 0)

            ret = line.find('rlc_blk_ptr')
            # this line contains downlink information
            if ret != -1:
                new_dl_bsn = int(line[26: line.find(' ', 26)])
                dl_bsns.append(new_dl_bsn)
                dl_bytes.append(dl_bytes[-1] + 37 if len(dl_bytes) > 0 else 37)
            else:
                if len(dl_bsns) > 0:
                    dl_bsns.append(dl_bsns[-1])
                dl_bytes.append(dl_bytes[-1] if len(dl_bytes) > 0 else 0)
            # print(dl_bytes[-1])

        start_time = timestamps[0]
        secs_elapsed = [(ele - start_time).total_seconds() for ele in timestamps]

        ul_gap = len(timestamps) - len(ul_bsns)
        ul_bsns = [ul_bsns[0] - 1] * ul_gap + ul_bsns

        dl_gap = len(timestamps) - len(dl_bsns)
        dl_bsns = [dl_bsns[0] - 1] * dl_gap + dl_bsns

        # draw ul and dl sequence number in one diagram
        plt.xlabel('secs elapsed')
        plt.ylabel('sequence number')
        plt.plot(secs_elapsed, ul_bsns, label='uplink')
        plt.plot(secs_elapsed, dl_bsns, label='downlink')
        plt.legend()
        plt.show()

        # draw ul and dl bytesin one diagram
        # plt.xlabel('secs elapsed')
        # plt.ylabel('#bytes')
        # plt.plot(secs_elapsed, ul_bytes, label='uplink')
        # plt.plot(secs_elapsed, dl_bytes, label='downlink')
        # plt.legend()
        # plt.show()
                