import serial
import time

if __name__ == '__main__':
    phy_ser_name = '/dev/ttyUSB0'
    baud_rate = 9600
    phy_ser = serial.Serial(phy_ser_name, baudrate=baud_rate, timeout=0, rtscts=True, dsrdtr=True)
    while True:
        print(phy_ser.readlines())
        phy_ser.write('at^spn=1\r\n'.encode('utf-8'))
        time.sleep(1)
    # with open('./strings_ril', 'r') as f:
    #     # commd = '^SYSINFO'
    #     while True:
    #         commd = f.readline()
    #         if len(commd) == 0:
    #             break
    #         if commd[0] == '^':
    #             print(commd)
    #             for trailing in ["", "=1", "=?", "?"]:
    #                 ret_code = phy_ser.write('at{0}{1}\r\n'.format(commd[:-1], trailing).encode('utf-8'))
    #                 response = phy_ser.readlines()
    #                 print(response)
    #                 if len(response) > 0:
    #                     print('response:', format(response))