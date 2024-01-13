import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import time
from time import strftime

# Create a class to plot sensor data //////
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
            time.sleep(0.010)
            data = self.ser.readline()
            while "\\n" not in str(data):
                time.sleep(0.001)
                temp = self.ser.readline()
                if temp.decode():
                    data = (data.decode() + temp.decode()).encode()
            data = data.decode().strip()
            data_values = data.split(", ")

            self.global_counter += 0.1
            self.sensor_values.append(float(data_values[4]))
            self.time_counter.append(self.global_counter)

        except (IndexError, UnicodeDecodeError, ValueError, KeyboardInterrupt) as e:
            print(f"Exception: {e}")

    # function to update plots on new sensor data
    def update_plot(self, frame):
        self.read_serial_data()
        plt.cla()
        plt.plot(self.time_counter, self.sensor_values, label="Sensor Value")
        plt.xlabel("Time [s]")
        plt.ylabel("Sensor")
        plt.legend()

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
        ani = FuncAnimation(fig, serial_plotter.update_plot, interval=2, save_count=5000)
        plt.show()

    except KeyboardInterrupt:
        serial_plotter.ser.close()

if __name__ == "__main__":
    main()


