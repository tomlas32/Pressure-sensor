import sys
import serial
import threading
import time
import csv
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import matplotlib.dates as mdates

class SerialReader(QObject):
    data_updated = pyqtSignal(float, float)

    def __init__(self, serial_port, baud_rate):
        super(SerialReader, self).__init__()
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.ser = None
        self.running = False
        self.data = []
        self.time_counter = []
        self.global_counter = 0

    def start_reading(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            self.running = True
            while self.running:
                self.ser.flushOutput()
                data = self.ser.readline().decode()
                while "\\n" not in str(data):
                    temp = self.ser.readline().decode().strip()
                    data_values = temp.split(", ")
                    if (len(data_values) == 5) and (data_values[4] != "Temperature"):
                        data_f = (float(data_values[4]))
                        self.global_counter += 0.1
                        self.data.append((self.global_counter, data_f))
                        self.data_updated.emit(self.global_counter, data_f)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
        except (IndexError, ValueError, TypeError):
            pass
        finally:
            if self.ser:
                self.ser.close()

    def stop_reading(self):
        self.running = False
        self.ser.close()

    def save_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['time', 'value'])
            csv_writer.writerows(self.data)

class RealTimePlotter(QMainWindow):
    def __init__(self, serial_port, baud_rate, parent=None):
        super(RealTimePlotter, self).__init__(parent)

        self.serial_port = serial_port
        self.baud_rate = baud_rate

        self.init_ui()
        self.init_serial()
        self.init_plot()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.canvas = FigureCanvas(plt.Figure())
        layout.addWidget(self.canvas)

        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_reading)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_reading)
        layout.addWidget(self.stop_button)

        self.save_button = QPushButton('Save to CSV', self)
        self.save_button.clicked.connect(self.save_to_csv)
        layout.addWidget(self.save_button)

        self.timer_n = None
        self.data = {'time': [], 'value': []}

        self.serial_reader = SerialReader(self.serial_port, self.baud_rate)
        self.serial_reader.data_updated.connect(self.update_plot)

    def init_serial(self):
        pass  # Serial initialization is now handled in SerialReader

    def init_plot(self):
        self.ax = self.canvas.figure.add_subplot(111)
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Real-Time Plot')

    def start_reading(self):
        self.timer_n = FuncAnimation(self.canvas.figure, lambda _: None, interval=100, save_count=5000)
        self.thread1 = threading.Thread(target=self.serial_reader.start_reading).start()

    def stop_reading(self):
        self.serial_reader.stop_reading()

    def save_to_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save to CSV', '', 'CSV Files (*.csv);;All Files (*)')
        if filename:
            self.serial_reader.save_to_csv(filename)

    def update_plot(self, timestamp, value):
        self.data['time'].append(timestamp)
        self.data['value'].append(value)

        self.line.set_data(self.data['time'], self.data['value'])
        self.ax.relim()
        self.ax.autoscale_view(True, True)
        self.canvas.draw()

    def closeEvent(self, event):
        self.stop_reading()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimePlotter(serial_port='COM4', baud_rate=9600)
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())
    