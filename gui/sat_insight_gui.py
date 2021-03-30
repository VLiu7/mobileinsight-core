# from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtWidgets import *
from mobile_insight.monitor import SatOfflineReplayer

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.monitor = SatOfflineReplayer()

    def init_ui(self):
        self.setFixedHeight(600)
        self.setFixedWidth(800)

        vbox = QVBoxLayout() 
        vbox.addWidget(QPushButton("button top"))

        hbox = QHBoxLayout()

        vbox_1 = QVBoxLayout()

        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(70000)
        self.table_widget.setColumnCount(4)
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