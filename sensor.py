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
            if self.ser.isOpen():
                self.ser.flushOutput()
                self.line = self.ser.readline().decode('utf-8').strip()
                if self.line:
                    self.timestamp = datetime.now().strftime('%H:%M:%S')
                    while "\\n" not in str(self.line):
                        self.temp = self.ser.readline()
                        if self.temp.decode():
                            self.data_read = (self.line.decode() + self.temp.decode()).encode()
                        self.data_read = self.data_read.decode().strip()
                    self.data_values = self.data_read.split(", ")
                    self.value = float(self.data_values[4])
                    self.data.append((self.timestamp, self.value))
                    return self.timestamp, self.value
        except serial.SerialException as e:
            raise serial.SerialException(f"Error reading from serial port: {e}")

    def close_serial_port(self):
        if self.ser:
            self.ser.close()

    def save_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            self.csv_writer = csv.writer(csvfile)
            self.csv_writer.writerow(['Time', 'Value'])
            self.csv_writer.writerows(self.data)
