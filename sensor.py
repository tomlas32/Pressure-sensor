import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
from datetime import datetime
from time import strftime
import time


class SerialCommunication:
    def __init__(self):
        self.ser = serial.Serial()
        self.data = []

    def open_serial_port(self, com_port):
        try:
            self.ser = serial.Serial(com_port, baudrate=9600, timeout=1)
        except serial.SerialException as e:
            raise serial.SerialException(f"Error opening {com_port}: {e}")

    def read_serial_data(self):
        try:
            self.ser.flushOutput()
            self.timestamp = datetime.now().strftime('%H:%M:%S')
            line = self.ser.readline().decode()
            if line:
                while "\\n" not in str(line):
                    temp = self.ser.readline().decode().strip()
                    data_values = temp.split(" ")
                    self.value = float(data_values[5])
                    self.data.append((self.timestamp, self.value))
            return self.data
        except serial.SerialException as e:
            raise serial.SerialException(f"Error reading from serial port: {e}")
        except IndexError:
            pass

    def close_serial_port(self):
        if self.ser:
            self.ser.close()

    def save_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            self.csv_writer = csv.writer(csvfile)
            self.csv_writer.writerow(['Time', 'Value'])
            self.csv_writer.writerows(self.data)
