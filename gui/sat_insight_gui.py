from PyQt5.QtWidgets import QApplication, QLabel
if __name__ == '__main__':
    app = QApplication([])
    label = QLabel("hello world")
    label.show()
    app.exec()