# from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from mobile_insight.monitor import OfflineMonitor 
from mobile_insight.analyzer import SatRlcAnalyzer
import datetime

class Worker(QObject):
    new_log  = pyqtSignal(object)
    def set_monitor(self, monitor):
        self.monitor = monitor
    def set_analyzer(self, analyzer):
        self.analyzer = analyzer
        self.analyzer.set_signal(self.new_log)
    def run(self):
        self.analyzer.set_source(self.monitor)
        self.monitor.run()

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.monitor = OfflineMonitor()
        self.monitor.set_input_path('Southeast_gate_ping.txt')
        self.analyzer = SatRlcAnalyzer()
        self.init_task()
    
    def init_task(self):
        self.thread = QThread()
        self.worker = Worker()
        self.worker.set_monitor(self.monitor)
        self.worker.set_analyzer(self.analyzer)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.new_log.connect(self.display_new_log)

        self.thread.start()

    def display_new_log(self, msg):
        row_index = self.analyzer.log_count - 1
        ts = msg.data.get_timestamp().strftime('%Y-%m-%d %H:%M:%S.%f') 
        gps_str = msg.data.get_gps()
        type_id = msg.type_id
        payload = msg.data.get_content()
        self.table_widget.setItem(row_index, 0, QTableWidgetItem(ts))
        self.table_widget.setItem(row_index, 1, QTableWidgetItem(type_id))
        self.table_widget.setItem(row_index, 2, QTableWidgetItem(gps_str))
        self.table_widget.setItem(row_index, 3, QTableWidgetItem(payload))


    def init_ui(self):
        self.setFixedHeight(600)
        self.setFixedWidth(800)

        vbox = QVBoxLayout() 
        vbox.addWidget(QPushButton("button top"))

        hbox = QHBoxLayout()

        vbox_1 = QVBoxLayout()

        self.table_widget = QTableWidget()
        header = self.table_widget.horizontalHeader()
        self.table_widget.setRowCount(70000)
        self.table_widget.setColumnCount(4)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_widget.setItem(0,0,QTableWidgetItem("Timestamp"))
        self.table_widget.setItem(0,1,QTableWidgetItem("Type ID"))
        self.table_widget.setItem(0,2,QTableWidgetItem("GPS"))
        self.table_widget.setItem(0,3,QTableWidgetItem("Content"))

        vbox_1.addWidget(self.table_widget)
        
        self.events = QTableWidget()
        self.events.setRowCount(10000)
        self.events.setColumnCount(2)
        self.events.setItem(0,0,QTableWidgetItem("Timestamp"))
        self.events.setItem(0,1,QTableWidgetItem("Event"))

        vbox_1.addWidget(self.events)

        hbox.addLayout(vbox_1)
        hbox.addWidget(QPushButton("button bottom right"))
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.show()


if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    app.exec()