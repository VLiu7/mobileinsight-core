import re
import numpy as np
import matplotlib.pyplot as plt

def draw_sub_plots(values, interval = 100, mark = True):
    for i in range(0, len(values), interval):
        if mark == False:
            plt.plot(np.arange(i, min(i + interval, len(values))), values[i: i + interval])
        else:
            plt.plot(np.arange(i, min(i + interval, len(values))), values[i: i + interval], marker = 'o')
        plt.get_current_fig_manager().full_screen_toggle()
        plt.xlabel('#no of line')
        plt.ylabel('signal strength(dBm)')
        plt.show()

if __name__ == '__main__':
    with open('sat_log_ping.txt') as f:
        lines = f.readlines()
        values = []
        for line in lines:
            ret = re.findall('-1[0-9]{2} ', line)
            if len(ret) != 0 and line.find('TIM') == -1:
                value = int(ret[0])
                if value > -130 and value < -110:
                    values.append(int(ret[0]))
        draw_sub_plots(values)