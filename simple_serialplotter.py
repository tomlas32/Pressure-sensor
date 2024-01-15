import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import time
from datetime import datetime
from time import strftime


# Create a class to plot sensor data //////
class SerialPlotter:
    def __init__(self, serial_port, baud_rate):
        self.ser = serial.Serial(serial_port, baud_rate, timeout=5)
        self.sensor_values = []
        self.time_counter = []
        self.global_counter = 0
        self.window_size = 5

    # funtion to read serial data
    def read_serial_data(self):
        try:
            self.ser.flushOutput()
            data = self.ser.readline()
            while "\\n" not in str(data):
                temp = self.ser.readline()
                if temp.decode():
                    data = (temp.decode()).encode()
                time.sleep(0.01)
            data = data.decode().strip()
            data_values = data.split(", ")

            self.global_counter += 0.1
            self.sensor_values.append(float(data_values[4]))
            self.smoothing_function()
            self.time_counter.append(self.global_counter)

        except (IndexError, UnicodeDecodeError, ValueError, KeyboardInterrupt):
            pass
    
    # function to smooth sensor data (moving average)
    def smoothing_function(self):
        if len(self.sensor_values) >= self.window_size:
            moving_average = sum(self.sensor_values[-self.window_size:]) / self.window_size
            #updates the last value in the list
            self.sensor_values[-1] = moving_average

    # function to update plots on new sensor data
    def update_plot(self, frame):
        self.read_serial_data()
        plt.cla()
        plt.plot(self.time_counter, self.sensor_values, label="Sensor Value")
        current_value_text = f"Current Value: {self.sensor_values[-1]:.2f}"
        plt.text(0.7, 1.1, current_value_text, transform=plt.gca().transAxes, 
                    fontsize=12, verticalalignment='top', horizontalalignment='right')
        plt.pause(0.01)
        plt.xlabel("Time [s]")
        plt.ylabel("Pressure [mbar]")

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

def main():
    try:
        #inititate serial port read instance
        serial_plotter = SerialPlotter(serial_port="COM4", baud_rate=9600)

        fig, ax = plt.subplots()
        #create callback logic closing the figure window and triggering csv save
        fig.canvas.mpl_connect("close_event", serial_plotter.save_to_csv)
        ani = FuncAnimation(fig, serial_plotter.update_plot, interval=5, save_count=5000)
        plt.show()

    except KeyboardInterrupt:
        serial_plotter.ser.close()

if __name__ == "__main__":
    main()


