import serial

if __name__ == '__main__':
    phy_ser_name = '/dev/ttyUSB0'
    baud_rate = 9600
    phy_ser = serial.Serial(phy_ser_name, baudrate=baud_rate, timeout=0, rtscts=True, dsrdtr=True)
    commd = '^SYSINFO'
    for trailing in ['', '=1', '=?', '?']:
        ret_code = phy_ser.write('at{0}{1}\r\n'.format(commd, trailing))
        print('ret_code={}'.format(ret_code))
        response = phy_ser.readlines()
        if len(response) > 0:
            print('response:', format(response))