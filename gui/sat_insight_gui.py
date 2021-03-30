# from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from mobile_insight.monitor import OfflineMonitor 
from mobile_insight.analyzer import SatRlcAnalyzer, SatL1Analyzer
import datetime

class Worker(QObject):
    new_log  = pyqtSignal(object)
    crc_error = pyqtSignal(object)
    out_of_receving_window = pyqtSignal(object)
    mcs = pyqtSignal(int)
    signal_strength = pyqtSignal(int)
    dl_rlc = pyqtSignal()
    def set_monitor(self, monitor):
        self.monitor = monitor
    def set_analyzers(self, analyzers):
        self.analyzers = analyzers
        rlc = self.analyzers["rlc"]
        rlc.set_signal("new_log", self.new_log)
        rlc.set_signal("crc_error", self.crc_error)
        rlc.set_signal("rejection", self.out_of_receving_window)
        rlc.set_signal("dl", self.dl_rlc)

        l1 = self.analyzers["l1"]
        l1.set_signal("mcs", self.mcs)
        l1.set_signal("signal_strength", self.signal_strength)
    def run(self):
        for analyzer in self.analyzers.values():
            analyzer.set_source(self.monitor)
        self.monitor.run()

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.monitor = OfflineMonitor()
        self.monitor.set_input_path('Southeast_gate_ping.txt')
        rlc = SatRlcAnalyzer()
        l1 = SatL1Analyzer()
        self.analyzers = {"rlc": rlc, "l1": l1}
        self.init_task()
    
    def init_task(self):
        self.event_cnt = 0
        self.thread = QThread()
        self.worker = Worker()
        self.worker.set_monitor(self.monitor)
        self.worker.set_analyzers(self.analyzers)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.new_log.connect(self.display_new_log)
        self.worker.crc_error.connect(self.display_new_event)
        self.worker.crc_error.connect(self.display_crc_error)
        self.worker.out_of_receving_window.connect(self.display_new_event)
        self.worker.mcs.connect(self.display_mcs)
        self.worker.signal_strength.connect(self.display_signal_strength)
        self.worker.dl_rlc.connect(self.dl_rlc_arrives)

        self.thread.start()

    def dl_rlc_arrives(self):
        # downlink rlcmac block arrives
        # update SMAC error
        self.display_crc_error()

    def display_crc_error(self):
        #TODO:
        error = self.analyzers["rlc"].error_block_cnt
        total = self.analyzers["rlc"].block_cnt
        self.mac_error_rate.setText("{}({} out ouf {})".format(
            error / total, 
            error, 
            total
        ))


    def display_signal_strength(self, signal_value):
        self.signal_value_label.setText(str(signal_value))

    def display_mcs(self, mcs_value):
        print("display mcs!")
        self.mcs_value_label.setText(str(mcs_value))

    def display_new_event(self, event):
        print("display new event")
        self.event_cnt += 1
        row_index = self.event_cnt
        ts = event.data.get_timestamp().strftime('%Y-%m-%d %H:%M:%S.%f') 
        payload = event.data.get_content()
        self.events.setItem(row_index, 0, QTableWidgetItem(ts))
        self.events.setItem(row_index, 1, QTableWidgetItem(payload))
        

    def display_new_log(self, msg):
        row_index = self.monitor.log_count
        ts = msg.data.get_timestamp().strftime('%Y-%m-%d %H:%M:%S.%f') 
        gps_str = msg.data.get_gps()
        type_id = msg.type_id
        payload = msg.data.get_content()
        self.table_widget.setItem(row_index, 0, QTableWidgetItem(ts))
        self.table_widget.setItem(row_index, 1, QTableWidgetItem(type_id))
        self.table_widget.setItem(row_index, 2, QTableWidgetItem(gps_str))
        self.table_widget.setItem(row_index, 3, QTableWidgetItem(payload))


    def init_ui(self):
        self.setFixedHeight(1000)
        self.setFixedWidth(1500)

        vbox = QVBoxLayout() 
        vbox.addWidget(QPushButton("button top"))

        hbox = QHBoxLayout()

        vbox_1 = QVBoxLayout()

        self.table_widget = QTableWidget()
        self.table_widget.setMaximumWidth(900)
        header = self.table_widget.horizontalHeader()
        self.table_widget.setRowCount(70000)
        self.table_widget.setColumnCount(4)
        # header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_widget.setItem(0,0,QTableWidgetItem("Timestamp"))
        self.table_widget.setItem(0,1,QTableWidgetItem("Type ID"))
        self.table_widget.setItem(0,2,QTableWidgetItem("GPS"))
        self.table_widget.setItem(0,3,QTableWidgetItem("Content"))

        vbox_1.addWidget(self.table_widget)
        
        self.events = QTableWidget()
        self.events.setMaximumWidth(900)
        self.events.setRowCount(10000)
        self.events.setColumnCount(2)
        self.events.setItem(0,0,QTableWidgetItem("Timestamp"))
        self.events.setItem(0,1,QTableWidgetItem("Event"))

        vbox_1.addWidget(self.events)

        hbox.addLayout(vbox_1)

        vbox_2 = QVBoxLayout()
        vbox_2.addWidget(QPushButton("RLC"))

        mac_layout = QVBoxLayout()
        mac_layout.addWidget(QLabel("MAC Layer"))
        mac_params = QHBoxLayout()
        # crc error
        self.mac_label = QLabel("CRC error rate: ")
        self.mac_error_rate = QLabel("--(-- out of --)")
        mac_params.addWidget(self.mac_label)
        mac_params.addWidget(self.mac_error_rate)
        mac_layout.addLayout(mac_params)
        vbox_2.addLayout(mac_layout)

        l1_layout = QVBoxLayout()
        l1_layout.addWidget(QLabel("Physical Layer"))
        l1_params = QHBoxLayout()
        # mcs
        self.mcs_label = QLabel("MCS value: ")
        self.mcs_value_label = QLabel("--")
        l1_params.addWidget(self.mcs_label)
        l1_params.addWidget(self.mcs_value_label)
        # signal strength
        self.signal_strength_label = QLabel("Signal Strength: ")
        self.signal_value_label = QLabel("--")
        l1_params.addWidget(self.signal_strength_label)
        l1_params.addWidget(self.signal_value_label)    
        l1_layout.addLayout(l1_params)
        vbox_2.addLayout(l1_layout)

        hbox.addLayout(vbox_2)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.show()


if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    app.exec()