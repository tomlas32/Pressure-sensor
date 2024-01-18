# -*- coding: utf-8 -*-
"""
Created on Tuesday, Jan  10 2024

This script is designed to plot pressure data coming from Arduino and MPR series pressure
sensor (read README for more details)

Make sure to adjust the COM parameters to your specific configuration

@author: Tomasz Lasota
version: 1.0

"""

import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import time
from time import strftime


# Create a class to plot sensor data 
class SerialPlotter:

    def __init__(self, serial_port, baud_rate):
        self.ser = serial.Serial(serial_port, baud_rate, timeout=5)
        self.sensor_values = []
        self.time_counter = []
        self.global_counter = 0

    # funtion to read serial data
    def read_serial_data(self):
        try:
            self.ser.flushOutput()
            data = self.ser.readline()
            if data:
                data = data.decode().strip()
                data_values = data.split(", ")
            self.global_counter += 0.11
            self.sensor_values.append(float(data_values[4]))
            self.time_counter.append(self.global_counter)

        except (IndexError, UnicodeDecodeError, ValueError, KeyboardInterrupt):
            pass

    # function to update plots and display current sensor value
    def update_plot(self, frame):
        try:
            self.read_serial_data()
            plt.cla()
            plt.plot(self.time_counter, self.sensor_values, label="Sensor Value")
            current_value_text = f"Current Value: {self.sensor_values[-1]:.2f}"
            plt.text(0.7, 1.1, current_value_text, transform=plt.gca().transAxes, 
                        fontsize=12, verticalalignment='top', horizontalalignment='right')
            plt.pause(0.01)
            plt.xlabel("Time [s]")
            plt.ylabel("Pressure [mbar]")
        except IndexError:
            pass

    # function to save data to csv
    def save_to_csv(self, event):
        current_time = strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        file_name = f"Pressure_readings_{current_time}.csv"

        with open(file_name, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Time", "Pressure reading"])
            for t, v in zip(self.time_counter, self.sensor_values):
                writer.writerow([t, v])

        self.ser.close()
        exit()

def main(COM_PORT):
    try:
        #inititate serial port read instance
        serial_plotter = SerialPlotter(serial_port=COM_PORT, baud_rate=9600)

        fig, ax = plt.subplots()
        #create callback logic closing the figure window and triggering csv save
        fig.canvas.mpl_connect("close_event", serial_plotter.save_to_csv)
        ani = FuncAnimation(fig, serial_plotter.update_plot, interval=5, save_count=5000)
        plt.show()

    except KeyboardInterrupt:
        serial_plotter.ser.close()

if __name__ == "__main__":

##################user defined COM port#######################################
    COM_PORT = "COM4"
##############################################################################
    main(COM_PORT)


