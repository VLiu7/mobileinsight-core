
if __name__ == '__main__':
    filename = 'sat_log_ping'
    with open('{0}.txt'.format(filename)) as f:
        ip_file = open('{0}_ip.txt'.format(filename), "w")
        rlc_file = open('{0}_rlc.txt'.format(filename), "w")
        smac_file = open('{0}_mac.txt'.format(filename), "w")
        lines = f.readlines()
        for line in lines:
            if line.find(' ip ') != -1:
                ip_file.writelines([line])
            elif line.find('SMAC') != -1:
                smac_file.writelines([line])
            elif line.find('RLC') != -1 or line.find('rlc') != -1:
                rlc_file.writelines([line])
        ip_file.close()
        rlc_file.close()
        smac_file.close()