import matplotlib.pyplot as plt

if __name__ == '__main__':
    with open('sandstorm_afternoon/shachen2_ping_ip.txt') as f:
        lines = f.readlines()
        bsns = []
        pdu_lengths = []
        out_of_window = []
        for line in lines:
            ret = line.find("RBID")
            if ret != -1:
                begin = line.find("BSN")
                end = line.find(",", begin)
                bsns.append(int(line[begin + 6:end]))
                out_of_window.append(0)
                begin = line.find("PDU length")
                pdu_lengths.append(int(line[begin + 13:]))
            ret = line.find('out of receiving window')
            if ret != -1:
                try:
                    out_of_window[-1] = 1
                except:
                    print('out of receiving window error without preceding dl rlcmac info!')
        print("{0:10.2f}% of downlink packets need retransmission".format(100 * sum(out_of_window) / len(out_of_window)))
        print(out_of_window)
        colors = [[1,0,0] if x == 1 else [0,1,0] for x in out_of_window]    # red for rejeceted, green for accepted
        for i in range(0, len(bsns), 100):
            plt.scatter(range(i, min(len(bsns), i+100)), bsns[i: i+100], c = colors[i: i+100], s = 10)
            plt.xlabel('#no of messages')
            plt.ylabel('block sequence number')
            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.title('下行序列号随时间变化(红色表示因为out of receiving window被拒绝的packet)')
            plt.show()
                