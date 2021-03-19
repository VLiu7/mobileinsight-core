import datetime
import numpy as np
import matplotlib.pyplot as plt

def draw_sub_plots(xs, ys, x_title, interval = 100, mark = True):
    for i in range(0, len(ys), interval):
        if mark == False:
            plt.plot(xs[i: i + interval], ys[i: i + interval])
        else:
            plt.plot(xs[i: i + interval], ys[i: i + interval], marker = 'o')
        plt.get_current_fig_manager().full_screen_toggle()
        plt.xlabel(x_title)
        plt.ylabel('has error')
        plt.show()

if __name__ == '__main__':
    with open('shachen2_ping_ip_mac.txt') as f:
        lines = f.readlines()
        timestamps = []
        has_error = []
        total_error = 0
        for line in lines:
            has_error.append(line.find('ERROR') != -1)
            total_error += (has_error[-1] == True)
            ts_str = line[1:20]
            # print('tr_str=', ts_str)
            ts_obj = datetime.datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            # print('ts_obj=', ts_obj)
            timestamps.append(ts_obj)
        start_time = timestamps[0]
        secs_elapsed = [(ele - start_time).total_seconds() for ele in timestamps]
        print('{} secs elapsed between 2 MAC errors in average'.format(secs_elapsed[-1] / total_error))
        # print('secs_elapsed:', secs_elapsed)
        # draw_sub_plots(timestamps, has_error, 'secs elasped', interval=len(has_error))
        # draw_sub_plots(np.arange(0,len(has_error)), has_error, '#no of line in mac subpart', interval=len(has_error))


