import re
import numpy as np
import matplotlib.pyplot as plt
import datetime

if __name__ == '__main__':
    with open('cloudy-connect-and-ping.txt') as f:
        lines = f.readlines()
        signals= []
        snrs = []
        start_time = None
        for (i, line) in enumerate(lines):
            # add timestamp
            ts_str = line[1:27]
            ts_obj = None
            try:
                ts_obj = datetime.datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S.%f')
            except:
                pass
            else:
                if start_time is None:
                    start_time = ts_obj
                msecs_elapsed = 1000 * (ts_obj - start_time).total_seconds()

                # match sat signal
                ret = re.findall('-1[0-9]{2} ', line)
                if len(ret) != 0 and line.find('TIM') == -1:
                    value = int(ret[0])
                    if value > -130 and value < -110:
                        signals.append((msecs_elapsed, int(ret[0])))
                # match snr
                ret = line.find('SNR=')
                if ret != -1:
                    end = line.find(' ', ret)
                    snr_value = int(line[ret + 4:end])
                    print('snr_value=', snr_value)
                    snrs.append((msecs_elapsed, snr_value))
        print(len(signals), len(snrs))

        n = 5
        # l1 = len(signals) // 5 
        # l2 = len(snrs) // 5 

        # for i in range(0, n):
        #     plt.plot(*zip(*signals[i * l1 : (i + 1) * l1]), label='signal strength')
        #     plt.plot(*zip(*snrs[i * l2 : (i + 1) * l2]), label='snr')
        #     plt.legend()
        #     plt.show()
                
        plt.plot(*zip(*signals), label='signal strength')
        plt.plot(*zip(*snrs), label='snr')
        plt.xlabel('msecs elapsed')
        plt.legend()
        plt.show()