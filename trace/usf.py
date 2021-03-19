if __name__ == '__main__':
    with open('shachen2_ping_walk.txt') as f:
        lines = f.readlines()
        usf_values = []
        for line in lines:
            ret = line.find('USF')
            if ret != -1:
                usf_values.append(int(line[ret + 4: ret + 6]))
        print(max(usf_values))
                