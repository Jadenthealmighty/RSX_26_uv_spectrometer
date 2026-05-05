import serial
import numpy as np
import matplotlib.pyplot as plt

import serial.tools.list_ports

plot_in_bkg = False

# IF you want to use the full plotting, uncomment the following line:
# note that this may only work on Mac and Linux

plot_in_bkg = True

# This will run plots in the background so you can input commands in terminal
# this uses the Qt backend, so you need to have PyQt installed

if plot_in_bkg:
    import sys
    import select
    import matplotlib
    matplotlib.use("QtAgg")
    from scipy.signal import find_peaks
    from scipy.signal import peak_widths


ports = serial.tools.list_ports.comports()

BAUD = 115200
ports = serial.tools.list_ports.comports()
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
y = np.zeros(NUM_PIXELS)
draw_sum = False


plt.ion()
fig, ax = plt.subplots(figsize=(8, 4))
line, = ax.plot(np.zeros(NUM_PIXELS), color = 'black', label= 'Spectra')
ax.set_ylim(0, 1000)
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Intensity")
plt.grid(True)

if plot_in_bkg:
    print("\n\n\n - Press t to toggle between summing and plotting")
    print(" - Press c to clear plot")
    print(" - Press q or Ctrl+C to quit")
    peak_scatter = ax.scatter([], [], color='green', s=40, label='Important points')

else:
    print("Listening on serial port... (Ctrl+C to quit)")

plt.legend()


def find_max(arr):
    return np.max(arr)

def plot_bkg_check():
    global draw_sum
    global summed
    if select.select([sys.stdin], [], [], 0)[0]:
        command = sys.stdin.readline().strip()
        if command == 't':
            if draw_sum:
                print("\nPlotting live data")
            else:
                print("\nPlotting summed data")
            draw_sum = not draw_sum
        if command == 'q':
            print("\nExiting...")
            ser.close()
            return False
        if command == 'c':
            print("\nClearing plot")
            summed = np.zeros(NUM_PIXELS)


            
            
    return True

try:
    while True:
        raw = ser.readline().decode('utf-8').strip()
        

        if not raw:
            continue
        try:
            data = np.array([float(x) for x in raw.split(',') if x.strip() != ''])
        except ValueError:
            print("WHAT")
            continue
        
        if plot_in_bkg:
            continues = plot_bkg_check()
            if not continues:
                break

        # Accumulate
        for i in range(min(len(data), NUM_PIXELS)):
            summed[i] += data[i]
        if draw_sum:
            summed_max = find_max(summed) / 1800 if find_max(summed) > 0 else 1
            y = summed / summed_max
        else:
            y = data[:NUM_PIXELS]

        line.set_ydata(y)
        line.set_xdata(x_ax_waves)
        ax.set_xlim(300, 900)
        ax.set_ylim(0, max(y) * 1.1 + 1)

        if plot_in_bkg:
            peaks, properties = find_peaks(data, height=100, distance=50)
            peak_x = x_ax_waves[peaks]
            peak_y = y[peaks]

            peak_scatter.set_offsets(np.c_[peak_x, peak_y])

            # TEST STARTS HERE
            # widths, width_heights, left_ips, right_ips = peak_widths(y, peaks, rel_height=0.5)

            # peaks_arr = np.abs(np.array(peak_x) - 530)
            # inds = peaks_arr.argmin()

            # delta = x_ax_waves[peaks[inds]] - x_ax_waves[peaks[inds] - 1]



            # print("\n\n\n\n\nPeak at:")
            # print(peak_x[inds])

            # print("\nWidth in px:")
            # print(widths[inds])
            # print("\nWidth in nm:")
            # print(widths[inds] * delta)
            
            # print(y[-4:])
            max_y = np.max(y)
            print('\nMax intensity: {}'.format(max_y))
            
            # TEST ENDS HERE

            fig.canvas.draw()
            fig.canvas.flush_events()
        else:
            plt.pause(0.001)
        

except KeyboardInterrupt:
    print("\nExiting...")
    ser.close()
