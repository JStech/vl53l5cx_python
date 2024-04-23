#!/usr/bin/env python3
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim

from vl53l5cx.vl53l5cx import VL53L5CX


driver = VL53L5CX()

alive = driver.is_alive()
if not alive:
    raise IOError("VL53L5CX Device is not alive")

print("Initialising...")
t = time.time()
driver.init()
print(f"Initialised ({time.time() - t:.1f}s)")

driver.set_resolution(8*8)
driver.set_ranging_frequency_hz(10)

# Ranging:
driver.start_ranging()

def on_press(event):
    global paused, fanim
    if event.key == " ":
        paused ^= True
        if paused:
            fanim.pause()
        else:
            fanim.resume()

fig = plt.figure()
fig.canvas.mpl_connect('key_press_event', on_press)
ax = fig.add_subplot(1, 1, 1)

im = ax.imshow(0.5 * np.eye(8))

previous_time = 0
loop = 0

def animate(i):
    global previous_time, loop
    if driver.check_data_ready():
        ranging_data = driver.get_ranging_data()

        # As the sensor is set in 4x4 mode by default, we have a total 
        # of 16 zones to print. For this example, only the data of first zone are 
        # print
        now = time.time()
        if previous_time != 0:
            time_to_get_new_data = now - previous_time
            print(f"Print data no : {driver.streamcount: >3d} ({time_to_get_new_data * 1000:.1f}ms)")
        else:
            print(f"Print data no : {driver.streamcount: >3d}")

        
        d = np.ndarray((8, 8), dtype='float64')
        for i in range(64):
            d[i//8, i%8] = ranging_data.distance_mm[driver.nb_target_per_zone * i] / 1000.

        im.set_array(d)

        previous_time = now
        loop += 1

    time.sleep(0.005)
    return (im,)

fanim = anim.FuncAnimation(fig, animate, blit=True)
plt.show()
