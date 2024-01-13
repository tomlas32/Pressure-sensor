import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
from datetime import datetime
from time import strftime


class SerialCommunication:
    def __init__(self):
        self.ser = None
        self.data = []

    def open_serial_port(self, com_port):
        try:
            self.ser = serial.Serial(com_port, baudrate=9600, timeout=1)
        except serial.SerialException as e:
            raise serial.SerialException(f"Error opening {com_port}: {e}")

    def read_serial_data(self):
        try:
            line = self.ser.readline().decode('utf-8').strip()
            if line:
                timestamp = datetime.now().strftime('%H:%M:%S')
                value = float(line)
                self.data.append((timestamp, value))
        except serial.SerialException as e:
            raise serial.SerialException(f"Error reading from serial port: {e}")

    def close_serial_port(self):
        if self.ser:
            self.ser.close()

    def save_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Timestamp', 'Value'])
            csv_writer.writerows(self.data)
