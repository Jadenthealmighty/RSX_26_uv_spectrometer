import numpy as np
import matplotlib.pyplot as plt
import serial.tools.list_ports

# Can delete later
import sys
import select
import addcopyfighandler


BAUD = 115200
ports = serial.tools.list_ports.comports()

# Serial port selection
PORT = ports[2].device
ser = serial.Serial(PORT, BAUD, timeout=1)

def wavelengths():
    A0 = 3.036826093e+2
    B1 = 2.705020455
    B2 = -1.12099836e-3
    B3 = -7.562738106e-6
    B4 = 8.1124198e-9
    B5 = 7.087599537e-12
    cl = lambda x: A0 +B1*(x+2) +B2*(x+2)**2 +B3*(x+2)**3 +B4*(x+2)**4 +B5*(x+2)**5
    nm = [int(cl(i+1.)) for i in range(288)]
    return np.array(nm)


x_ax_waves = wavelengths()
NUM_PIXELS = 288
summed = np.zeros(NUM_PIXELS)
draw_sum = False


plt.ion()
fig, ax = plt.subplots(figsize=(8, 4))
line, = ax.plot(np.zeros(NUM_PIXELS), color = 'black', label= 'Spectra')
ax.set_ylim(0, 1000)
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Intensity")
plt.grid(True)

print("Listening on serial port... (Ctrl+C to quit)")
print("Press b to copy plot")

plt.legend()


def find_max(arr):
    return np.max(arr)


try:
    while True:
        raw = ser.readline().decode('utf-8').strip()
        
        # Reading
        if not raw:
            continue
        try:
            data = np.array([int(x) for x in raw.split(',') if x.strip() != ''])
        except ValueError:
            print("WHAT")
            continue

        # Accumulation
        for i in range(min(len(data), NUM_PIXELS)):
            summed[i] += data[i]
        if draw_sum:
            summed_max = find_max(summed) / 1800 if find_max(summed) > 0 else 1
            y = summed / summed_max
        else:
            y = data[:NUM_PIXELS]
        
        if select.select([sys.stdin], [], [], 0)[0]:
            command = sys.stdin.readline().strip()
            if command == 'b':
                print("You have 10 seconds to copy the plot")
                plt.pause(10)
                continue


        line.set_ydata(y)
        line.set_xdata(x_ax_waves)
        ax.set_xlim(300, 900)
        ax.set_ylim(0, max(y) * 1.1 + 1)
        plt.pause(0.01)
        

except KeyboardInterrupt:
    print("\nExiting...")
    ser.close()
