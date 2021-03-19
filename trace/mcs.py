import matplotlib.pyplot as plt
import numpy as np


def get_mcs_values(filename):
    with open(filename) as f:
        lines = f.readlines()
        mcs_values = []
        for line in lines:
            ret = line.find('MCS')
            if ret != -1:
                mcs_values.append(int(line[ret + 4]))
        return mcs_values

def draw_sub_plots(values, interval = 100, mark = True):
    for i in range(0, len(values), interval):
        if mark == False:
            plt.plot(np.arange(i, min(i + interval, len(values))), values[i: i + interval])
        else:
            plt.plot(np.arange(i, min(i + interval, len(values))), values[i: i + interval], marker = 'o')
        plt.get_current_fig_manager().full_screen_toggle()
        plt.show()

def draw_sub_plot(values, count, start = 0, mark = True):
    if mark == False:
        plt.plot(np.arange(start, start + count), values[start: start+count])
    else:
        plt.plot(np.arange(start, start + count), values[start: start+count], marker = 'o')

    plt.get_current_fig_manager().full_screen_toggle()
    plt.show()

if __name__ == '__main__':
        values = get_mcs_values('shachen2_ping_walk.txt')
        print(len(values))
        draw_sub_plots(values, 100, mark=True)