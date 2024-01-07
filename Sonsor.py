import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import time


# define variables
SERIAL_PORT = "COM4"
BAUD_RATE = 9600                                                    #read counter
x = 0
# initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5)

# initialize lists for data storage
#x_time = []
value1_data = []

# define function for data read and processing
def serialRead():
    try:
        ser.flushOutput()
        time.sleep(.010)
        data = ser.readline()
        # check for end of line \n character
        while not "\\n" in str(data):
            time.sleep(.001)
            temp = ser.readline()
            if not not temp.decode():                               #check if temp is not empty the decode
                data = (data.decode() + temp.decode()).encode()     #encoding needed as long values might need multiple passes     
        data = data.decode().strip()
        dataValues = data.split(", ")

        #print(data)
        value1_data.append(float(dataValues[4]))
        #print(value1_data)
    except(IndexError, UnicodeDecodeError, ValueError, KeyboardInterrupt):
        pass

# define a function for plot update
def plotUpdate(frame):
    serialRead()
    plt.cla()
    plt.plot(value1_data, label = "Value 1")
    plt.xlabel("Read counter")
    plt.ylabel("Sensor")
    plt.legend()

def on_close(event):                                                #define a function for saving data into csv 
    with open("data.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Value 1"])
        for v1, in zip(value1_data):
            writer.writerow([v1])
    exit()

try:
    fig, ax = plt.subplots()
    fig.canvas.mpl_connect("close_event", on_close)                    #create callback logic closing the figure window and triggering csv save
    ani_plot = FuncAnimation(fig, plotUpdate, interval=2)
    plt.show()
except(KeyboardInterrupt):
    pass
       

