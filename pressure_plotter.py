# -*- coding: utf-8 -*-
"""
Created on Tuesday, Jan  10 2024

This script is designed to plot pressure data coming from Arduino and MPR series pressure
sensor (read README for more details)

Make sure to adjust the COM parameters to your specific configuration

Version changes:
Version 1.0 - first release
Version 1.1 - rewored the constructor to include initialization of the plot animation 
              to prevent flashing labels

@author: Tomasz Lasota
version: 1.1

"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
import time
import csv

class SerialPlotter:
    def __init__(self, serial_port, baud_rate):
        self.ser = serial.Serial(serial_port, baud_rate, timeout=5)
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [])
        self.text = self.ax.text(0.7, 1.1, "", transform=self.ax.transAxes,
                                 fontsize=12, verticalalignment='top', horizontalalignment='right')
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Pressure [mbar]")

        # Create callback logic closing the figure window and triggering CSV save
        self.fig.canvas.mpl_connect("close_event", self.save_to_csv)

        self.sensor_values = []
        self.time_counter = []
        self.global_counter = 0

        # Set up animation
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=5)

        plt.show()
    # function to read and parse serial port data 
    def read_serial_data(self):
        try:
            data = self.ser.readline()
            if data:
                data = data.decode().strip()
                data_values = data.split(", ")
                self.global_counter += 0.11
                return self.global_counter, float(data_values[4])

        except (IndexError, UnicodeDecodeError, ValueError, KeyboardInterrupt):
            return None
    # function updating the animation plot with new serial data
    def update_plot(self, frame):
        data = self.read_serial_data()
        if data is not None:
            time_val, sensor_val = data
            self.time_counter.append(time_val)
            self.sensor_values.append(sensor_val)

            if len(self.time_counter) > 0:
                self.line.set_data(self.time_counter, self.sensor_values)
                current_value_text = f"Current Value: {self.sensor_values[-1]:.2f}"
                self.text.set_text(current_value_text)

                # Explicitly set plot limits
                self.ax.set_xlim(min(self.time_counter), max(self.time_counter))
                self.ax.set_ylim(min(self.sensor_values) - 30, max(self.sensor_values) +50)
                plt.pause(0.01)
            else:
                print(f"No data to plot")

    # function for auto save of pressure readings data into csv
    def save_to_csv(self, event):
        self.ser.close()
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"Pressure_readings_{current_time}.csv"

        with open(file_name, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Time", "Pressure reading"])
            for t, v in zip(self.time_counter, self.sensor_values):
                writer.writerow([t, v])

        exit()

if __name__ == "__main__":
    COM_PORT = "COM9"
    baud_rate = 9600
    serial_plotter = SerialPlotter(COM_PORT, baud_rate)
