import numpy as np
import matplotlib.pyplot as plt

data = np.load("output_array.npy")

integrate_info = np.load("integrate_info.npy")

std = np.std(data, axis=1)
mean = np.mean(data, axis=1)


as_pct = std / mean * 100


print(std)
print(mean)

tot_std = np.mean(std)
print(f"Total standard deviation: {tot_std}")

print('\n\n\n')
print(integrate_info)

pixels = np.arange(288)

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


plt.errorbar(x_ax_waves, mean, yerr=std, fmt='o', label='Mean')
# plt.axhline(y=0, color='black')

dif = np.gradient(x_ax_waves)

plt.figure()
plt.plot(x_ax_waves, std)
plt.axhline(y=tot_std, color = 'red')
plt.figure()
plt.plot(x_ax_waves, as_pct)
plt.show()