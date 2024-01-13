import serial
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import csv
from datetime import datetime

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

class SerialPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Monitor")

        # Variables
        self.com_port_var = tk.StringVar()
        self.serial_communication = SerialCommunication()

        # GUI Components
        self.create_widgets()

    def create_widgets(self):
        # COM Port Selection
        com_label = ttk.Label(self.root, text="Select COM Port:")
        com_label.grid(row=0, column=0, padx=10, pady=10)

        com_combobox = ttk.Combobox(self.root, textvariable=self.com_port_var)
        com_combobox.grid(row=0, column=1, padx=10, pady=10)
        com_combobox['values'] = [f"COM{x}" for x in range(1, 10)]

        # Plotting
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Start/Stop Button
        start_button = ttk.Button(self.root, text="Start", command=self.start_plotting)
        start_button.grid(row=2, column=0, pady=10)

        stop_button = ttk.Button(self.root, text="Stop", command=self.stop_plotting)
        stop_button.grid(row=2, column=1, pady=10)

    def start_plotting(self):
        com_port = self.com_port_var.get()

        try:
            self.serial_communication.open_serial_port(com_port)
            self.root.after(100, self.read_and_plot_data)
        except serial.SerialException as e:
            print(e)  # You can handle errors as appropriate

    def read_and_plot_data(self):
        self.serial_communication.read_serial_data()
        self.plot_data()
        self.root.update_idletasks()
        self.root.after(100, self.read_and_plot_data)

    def stop_plotting(self):
        self.serial_communication.close_serial_port()
        self.save_to_csv()

    def save_to_csv(self):
        filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.serial_communication.save_to_csv(filename)

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialPlotterApp(root)
    root.mainloop()