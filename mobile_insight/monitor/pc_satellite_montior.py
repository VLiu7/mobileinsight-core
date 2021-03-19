#!/usr/bin/python
# Filename: pc_satellite_monitor.py
"""
pc_satellite_monitor.py
"""

__all__ = ["PCSatelliteMonitor"]

from .monitor import Monitor, Event
import serial
import sys
import os
import timeit
import time
from datetime import datetime

class PCSatelliteMonitor(Monitor):
    """
    A PC-side monitor for tdgcore satellite phone logs
    """

    #TODO:a list containing the currently supported message types.
    SUPPORTED_TYPES = {}

    def __init__(self):
        Monitor.__init__(self)
        self.phy_baudrate = 9600
        self.phy_ser_name = None
        self.log_path = None
        self.log_enabled = True

    def set_serial_port(self, phy_ser_name):
        """
        Configure the serial port that dumps messages

        :param phy_ser_name: the serial port name (path)
        :type phy_ser_name: string
        """
        self.phy_ser_name = phy_ser_name

    def set_baudrate(self, rate):
        """
        Configure the baudrate of the serial port

        :param rate: the baudrate of the port
        :type rate: int
        """
        self.phy_baudrate = rate

    def available_log_types(self):
        """
        Return available log types

        :returns: a list of supported message types
        """
        return self.__class__.SUPPORTED_TYPES

    def disable_logs(self):
        self.log_enabled = False
        
    def enable_logs(self):
        self.log_enabled = True

    def enable_log(self, type_name):
        """
        Enable the messages to be monitored.
        :param type_name: the message type(s) to be monitored
        :type type_name: string or list

        :except ValueError: unsupported message type encountered
        """
        cls = self.__class__
        if isinstance(type_name, str):
            type_name = [type_name]
        for n in type_name:
            if n not in cls.SUPPORTED_TYPES:
                self.log_warning("Unsupported log message type: %s" % n)
            if n not in self._type_names:
                self._type_names.append(n)
                self.log_info("Enable collection: " + n)
        #TODO: save type_name for future filter

    def enable_log_all(self):
        """
        Enable all supported logs
        """
        cls = self.__class__
        self.enable_log(cls.SUPPORTED_TYPES)

    def save_log_as(self, path):
        """
        Save the log for offline analysis

        :param path: the file name to be saved
        :type path: string
        :param log_types: a filter of message types to be saved
        :type log_types: list of string
        """
        self.log_path = path

    def run(self):
        """
        Start monitoring the satellite network. This is usually the entrance of monitoring and analysis.

        This function does NOT return or raise any exception.
        """
        assert self.phy_ser_name

        print(("PHY COM: %s" % self.phy_ser_name))
        print(("PHY BAUD RATE: %d" % self.phy_baudrate))

        log_file = None
        try:
            # Open COM ports
            log_file = open(os.path.join('./logs', self.log_path), "w")
            phy_ser = serial.Serial(self.phy_ser_name,
                                    baudrate=self.phy_baudrate,
                                    timeout=None, rtscts=True, dsrdtr=True)

            presult=phy_ser.write('at^POSREQ=?\r\n'.encode("utf-8"))
            print('total bits sended:'+str(presult))

            # Read log packets from serial port and decode their contents
            while True:
                s = phy_ser.readline()
                if len(s) > 0:
                    print('['+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))+"],",end='')
                    print(s.decode('utf-8'),end='')
                    # send event to analyzers
                    # TODO: type_id is currently None, and packet is a copy of line read from serial-port
                    # event = Event(timeit.default_timer(), 
                    #        None, 
                    #        s)
                    # self.send(event)
                    # write one line to log file
                    #log_file.writeline(s.decode('utf-8'))
                    #log_file.flush()
        except (KeyboardInterrupt, RuntimeError) as e:
            print(("\n\n%s Detected: Disabling all logs" % type(e).__name__))
            phy_ser.close()
            #TODO: disable all logs 
            sys.exit(e) 
        except Exception as e:
            sys.exit(e)
        finally:
            if log_file is not None:
                log_file.close()

# test
if __name__ == '__main__':
    src = PCSatelliteMonitor()
    src.set_serial_port('/dev/ttyUSB0')
    src.set_baudrate(9600)
    src.save_log_as('./pc_sat_monitor.log')
    src.run()
