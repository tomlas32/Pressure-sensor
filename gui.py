import serial
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
from sensor import SerialCommunication
import serial.tools.list_ports as stlp




class SerialPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Monitor")

        # Variables
        self.com_port_var = tk.StringVar()
        self.serial_communication = SerialCommunication()

        # Initilize GUI Components
        self.create_widgets()
    
    # get all active COM ports
    def get_active_com(self):
        self.available_ports = [port.device for port in stlp.comports()]
        return self.available_ports
    
    def current_pressure(self):
        x = self.serial_communication.read_serial_data()
        print(x)
        if self.serial_communication.data:
            print("Current pressure")
            time, value = zip(*self.serial_communication.data)
            self.s_current_value.config(text= value[-1])
        self.s_current_value.after(100, self.current_pressure) # update the value every 10 miliseconds
    
    # create the GUI components
    def create_widgets(self):
        # COM Port Selection
        com_label = ttk.Label(self.root, text="Select COM Port:")
        com_label.grid(row=0, column=0, padx=10, pady=10)

        # dropdown menu
        com_combobox = ttk.Combobox(self.root, textvariable=self.com_port_var)
        com_combobox.grid(row=0, column=1, padx=10, pady=10)
        com_combobox['values'] = self.get_active_com()

        # Current sensor value label
        sensor_label = ttk.Label(self.root, text="Current Sensor Value:")
        sensor_label.grid(row=0, column=2, padx=10, pady=5)

        # Current sensor value
        self.s_current_value = ttk.Label(self.root, text="0.000", font=("Helvetica", 16))
        self.s_current_value.grid(row=1, column=2, padx=10, pady=5, sticky="n")

        # Plotting
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Pressure (mbar)')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Start/Stop Button
        start_button = ttk.Button(self.root, text="Start", command=self.start_plotting)
        start_button.grid(row=2, column=0, pady=10)

        stop_button = ttk.Button(self.root, text="Stop", command=self.stop_plotting)
        stop_button.grid(row=2, column=1, pady=10)

    def read_and_plot_data(self):
        self.serial_communication.read_serial_data()
        if self.serial_communication.data:
            time, value = zip(*self.serial_communication.data)
            self.ax.clear()
            self.ax.plot(time, value)
            self.root.update_idletasks()
            self.canvas.draw()
        
        self.root.after(100, self.read_and_plot_data) # triggers the function every 10 miliseconds
    
    def start_plotting(self):
        
        try:
            com_port = self.com_port_var.get()
            self.serial_communication.open_serial_port(com_port)
            #self.read_and_plot_data()
            self.current_pressure()
        except serial.SerialException as e:
            print(e)  # You can handle errors as appropriate

    def stop_plotting(self):
        self.serial_communication.close_serial_port()
        self.save_to_csv()

    def save_to_csv(self):
        filename = f"data_{datetime.now().strftime('%Y%m%d %H%M%S')}.csv"
        self.serial_communication.save_to_csv(filename)

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialPlotterApp(root)
    root.mainloop()