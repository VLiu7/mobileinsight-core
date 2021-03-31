# from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from mobile_insight.monitor import OfflineMonitor 
from mobile_insight.analyzer import SatRlcAnalyzer, SatL1Analyzer
import datetime
import pyqtgraph as pg
from pyqtgraph import plot, PlotWidget
from PyQt5.QtGui import *

class Worker(QObject):
    new_log  = pyqtSignal(object)
    crc_error = pyqtSignal(object)
    out_of_receving_window = pyqtSignal(object)
    mcs = pyqtSignal(int)
    signal_strength = pyqtSignal(int)
    dl_rlc = pyqtSignal()
    update_dl_rate = pyqtSignal(object)
    update_ul_rate = pyqtSignal(object)

    def set_monitor(self, monitor):
        self.monitor = monitor
    def set_analyzers(self, analyzers):
        self.analyzers = analyzers
        rlc = self.analyzers["rlc"]
        rlc.set_signal("new_log", self.new_log)
        rlc.set_signal("crc_error", self.crc_error)
        rlc.set_signal("rejection", self.out_of_receving_window)
        rlc.set_signal("dl", self.dl_rlc)
        rlc.set_signal("update_dl_rate", self.update_dl_rate)
        rlc.set_signal("update_ul_rate", self.update_ul_rate)

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
        self.worker.out_of_receving_window.connect(self.display_rejection_rate)
        self.worker.mcs.connect(self.display_mcs)
        self.worker.signal_strength.connect(self.display_signal_strength)
        self.worker.dl_rlc.connect(self.dl_rlc_arrives)
        self.worker.update_dl_rate.connect(self.display_dl_rate)
        self.worker.update_ul_rate.connect(self.display_ul_rate)

        self.thread.start()
    
    def display_graph(self):
        self.line_dl.setData(self.analyzers["rlc"].timestamps,
                             self.analyzers["rlc"].dl_rates)
        self.line_ul.setData(self.analyzers["rlc"].ul_timestamps,
                             self.analyzers["rlc"].ul_rates)

    def display_duplicate_rate(self):
        self.duplicate_rate_value_label.setText("{} % ({} out of {})".format(
            (self.rejection_rate_value - self.error_rate_value) * 100,
            int(self.analyzers["rlc"].block_cnt * (self.rejection_rate_value - self.error_rate_value)),
            self.analyzers["rlc"].block_cnt
        ))

    def display_rejection_rate(self, obj):
        error_cnt = self.analyzers["rlc"].rejection_block_cnt
        total = self.analyzers["rlc"].block_cnt
        self.rejection_rate_value = error_cnt / total
        self.rejection_rate_value_label.setText("{} %({} out of {})".format(
            error_cnt / total * 100,
            error_cnt,
            total
        ))
        self.display_duplicate_rate()

    def display_ul_rate(self, obj):
        secs = obj["secs"]
        ul_bytes = obj["bytes"]
        instant_rate = ul_bytes / secs 
        self.ul_rate_value_label.setText("{0:10.2f} bytes / s ({} bytes in latest {}s)".format(
            ul_bytes / secs,
            ul_bytes,
            secs,
        ))
        self.display_graph()

    def display_dl_rate(self, obj):
        secs = obj["secs"]
        dl_bytes = obj["bytes"]
        instant_rate = dl_bytes / secs 
        self.dl_rate_value_label.setText("{} bytes / s ({} bytes in latest {}s)".format(
            dl_bytes / secs,
            dl_bytes,
            secs,
        ))
        self.display_graph()

    def dl_rlc_arrives(self):
        # downlink rlcmac block arrives
        # update SMAC error
        self.display_crc_error()

    def display_crc_error(self):
        # MAC Layer
        error = self.analyzers["rlc"].error_block_cnt
        total = self.analyzers["rlc"].block_cnt
        self.error_rate_value = error / total
        self.mac_error_rate.setText("{} %({} out ouf {})".format(
            error / total * 100, 
            error, 
            total
        ))
        self.display_duplicate_rate()

        # RLC layer
        self.error_rate_value_label.setText("{} % ({} out of {})".format(
            error / total * 100,
            error,
            total 
        ))


    def display_signal_strength(self, signal_value):
        self.signal_value_label.setText(str(signal_value))
        self.display_sig_graph()

    def display_sig_graph(self):
        self.line_sig.setData(self.analyzers["l1"].signal_timestamps,
                              self.analyzers["l1"].signal_values)

    def display_mcs(self, mcs_value):
        # print("display mcs!")
        self.mcs_value_label.setText(str(mcs_value))
        self.display_mcs_graph()

    def display_mcs_graph(self):
        self.line_mcs.setData(self.analyzers["l1"].mcs_timestamps,
                              self.analyzers["l1"].mcs_values)

    def display_new_event(self, event):
        # print("display new event")
        self.event_cnt += 1
        row_index = self.event_cnt
        ts = event.data.get_timestamp().strftime('%Y-%m-%d %H:%M:%S.%f') 
        payload = event.data.get_content()
        description = None 
        if payload.find("out of") != -1:
            description = "Downlink block is rejected!"
        elif payload.find("CRC") != -1:
            description = "Downlink block failed CRC check!" 
        self.events.setItem(row_index, 0, QTableWidgetItem(ts))
        self.events.setItem(row_index, 1, QTableWidgetItem(description))
        self.events.setItem(row_index, 2, QTableWidgetItem(payload))

        last_item = self.events.item(row_index, 0)
        self.events.scrollToItem(last_item, QAbstractItemView.PositionAtBottom)
        

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
        last_item = self.table_widget.item(row_index, 0)
        self.table_widget.scrollToItem(last_item, QAbstractItemView.PositionAtBottom)


    def init_ui(self):
        self.setFixedHeight(1000)
        self.setFixedWidth(1500)

        vbox = QVBoxLayout() 
        vbox.addWidget(QPushButton("button top"))

        hbox = QHBoxLayout()

        vbox_1 = QVBoxLayout()

        self.table_widget = QTableWidget()
        self.table_widget.setMaximumWidth(700)
        self.table_widget.setMinimumWidth(700)
        header = self.table_widget.horizontalHeader()
        self.table_widget.setRowCount(70000)
        self.table_widget.setColumnCount(4)
        # header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_widget.setItem(0,0,QTableWidgetItem("Timestamp"))
        self.table_widget.setItem(0,1,QTableWidgetItem("Type ID"))
        self.table_widget.setItem(0,2,QTableWidgetItem("GPS"))
        self.table_widget.setItem(0,3,QTableWidgetItem("Content"))

        vbox_1.addWidget(self.table_widget)
        
        self.events = QTableWidget()
        self.events.setMaximumWidth(900)
        self.events.setRowCount(10000)
        self.events.setColumnCount(3)
        header = self.events.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.events.setItem(0,0,QTableWidgetItem("Timestamp"))
        self.events.setItem(0,1,QTableWidgetItem("Description"))
        self.events.setItem(0,2,QTableWidgetItem("Message"))

        vbox_1.addWidget(self.events)

        hbox.addLayout(vbox_1)

        vbox_2 = QVBoxLayout()
        rlc_layout = QVBoxLayout()
        rlc_layout.addWidget(QLabel("RLC Layer"))
        rlc_params = QHBoxLayout()

        rlc_rate = QVBoxLayout()
        # dl rate
        dl_rate = QHBoxLayout()
        self.dl_rate_label = QLabel("Downlink rate: ")
        self.dl_rate_value_label = QLabel("-- bytes / s (-- bytes in latest --s)")
        dl_rate.addWidget(self.dl_rate_label)
        dl_rate.addWidget(self.dl_rate_value_label)
        rlc_rate.addLayout(dl_rate)
        # ul rate
        ul_rate = QHBoxLayout()
        self.ul_rate_label = QLabel("Uplink rate: ")
        self.ul_rate_value_label = QLabel("-- bytes / s (-- bytes in latest --s)")
        ul_rate.addWidget(self.ul_rate_label)
        ul_rate.addWidget(self.ul_rate_value_label)
        rlc_rate.addLayout(ul_rate)
        # plot
        self.graph = pg.PlotWidget()
        rlc_rate.addWidget(self.graph)
        self.graph.addLegend()
        self.line_ul = pg.PlotCurveItem(clear=True, pen="r", name = "Uplink")
        self.line_dl = pg.PlotCurveItem(clear=True, pen="y", name = "Downlink")
        self.graph.addItem(self.line_ul)
        self.graph.addItem(self.line_dl)

        rlc_params.addLayout(rlc_rate)

        abnormal_rates = QVBoxLayout()
        # rejection rate
        rejection_rate = QHBoxLayout()
        self.rejection_rate_label = QLabel("Rejection rate: ")
        self.rejection_rate_value_label = QLabel("-- % (-- out of --)")
        rejection_rate.addWidget(self.rejection_rate_label)
        rejection_rate.addWidget(self.rejection_rate_value_label)
        abnormal_rates.addLayout(rejection_rate)
        # error rate
        error_rate = QHBoxLayout()
        self.error_rate_label = QLabel("CRC error rate: ")
        self.error_rate_value_label = QLabel("-- % (-- out of --)")
        error_rate.addWidget(self.error_rate_label)
        error_rate.addWidget(self.error_rate_value_label)
        abnormal_rates.addLayout(error_rate)
        # duplicate rate
        duplicate_rate = QHBoxLayout()
        self.duplicate_rate_label = QLabel("Duplicate rate: ")
        self.duplicate_rate_value_label = QLabel("-- % (-- out of --)")
        duplicate_rate.addWidget(self.duplicate_rate_label)
        duplicate_rate.addWidget(self.duplicate_rate_value_label)
        abnormal_rates.addLayout(duplicate_rate)
        
        
        rlc_params.addLayout(abnormal_rates)

        rlc_layout.addLayout(rlc_params)
        vbox_2.addLayout(rlc_layout)

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
        mcs_layout = QVBoxLayout()
        mcs_text = QHBoxLayout()
        mcs_layout.addLayout(mcs_text)
        self.mcs_label = QLabel("MCS value: ")
        self.mcs_value_label = QLabel("--")
        mcs_text.addWidget(self.mcs_label)
        mcs_text.addWidget(self.mcs_value_label)
        l1_params.addLayout(mcs_layout)
        self.mcs_graph = pg.PlotWidget()
        mcs_layout.addWidget(self.mcs_graph)
        self.mcs_graph.addLegend()
        self.line_mcs = pg.PlotCurveItem(clear=True, pen="y")
        self.mcs_graph.addItem(self.line_mcs)
        l1_params.addLayout(mcs_layout)
        # signal strength
        sig_layout = QVBoxLayout()
        sig_text = QHBoxLayout()
        self.signal_strength_label = QLabel("Signal Strength: ")
        self.signal_value_label = QLabel("--")
        sig_text.addWidget(self.signal_strength_label)
        sig_text.addWidget(self.signal_value_label)
        sig_layout.addLayout(sig_text)
        self.sig_graph = pg.PlotWidget()
        sig_layout.addWidget(self.sig_graph)
        self.sig_graph.addLegend()
        self.line_sig = pg.PlotCurveItem(clear=True, pen="y")
        self.sig_graph.addItem(self.line_sig)

        l1_params.addLayout(sig_layout)
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