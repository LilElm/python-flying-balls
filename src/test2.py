from PyQt5.QtCore import QThread, QTimer, pyqtSignal, QRunnable
from PyQt5.QtWidgets import QApplication
import sys

#class Worker(QThread):
class Worker(QRunnable):

    def __init__(self):
        super().__init__()

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.work)
        self.timer.start(1000)  # Emit the timeout() signal every second

    def work(self):
        print("Timer triggered")
        #self.signal.emit()

class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.worker = Worker()
        self.worker.run()

if __name__ == "__main__":
    app = App(sys.argv)
    sys.exit(app.exec_())
