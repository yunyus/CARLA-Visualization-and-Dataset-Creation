import pandas as pd
import os
import time
import re
import math
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image

# Read the Excel file
data = pd.read_excel('data.xlsx')

# Create a unique folder for each run
output_folder = 'output_' + str(time.time())
os.makedirs(output_folder, exist_ok=True)

max_tick = data['Tick'].max()
accels = []
speeds = []
images = []
t = []

# Iterate over each tick value
for tick in data['Tick'].unique():

    t.append(tick)

    tick_data = data[data['Tick'] == tick]

    vehicles = tick_data[tick_data['Type'] == 'Vehicle']

    for index, vehicle in vehicles.iterrows():

        speed_cur = vehicle['Speed']
        spd = 0
        spd_comp = []
        match = re.search(r'x=(-?\d+\.\d+), y=(-?\d+\.\d+), z=(-?\d+\.\d+)', speed_cur)
        if match:
            x, y, z = match.groups()
            x, y, z = float(x), float(y), float(z)
            spd = math.sqrt(x ** 2 + y ** 2 + z ** 2)
            spd_comp = [x, y, z]

            speeds.append(spd)

        acc_cur = vehicle['Acceleration']
        acc = 0
        acc_comp = []
        match = re.search(r'x=(-?\d+\.\d+), y=(-?\d+\.\d+), z=(-?\d+\.\d+)', acc_cur)
        if match:
            x, y, z = match.groups()
            x, y, z = float(x), float(y), float(z)
            acc = math.sqrt(x ** 2 + y ** 2 + z ** 2)
            acc_comp = [x, y, z]

            # Dot Product for acc_comp and spd_comp
            dot = np.dot(acc_comp, spd_comp)

            if (dot < 0):
                acc *= -1

            accels.append(acc)

    # Create a pandas DataFrame to hold the data
    datas = pd.DataFrame({'Time': t, 'Velocity': speeds, 'Acceleration': accels})

    # Set the seaborn style
    sns.set(style='darkgrid')

    # Create the line plot
    sns.lineplot(data=datas, x='Time', y='Velocity', label='Velocity')
    sns.lineplot(data=datas, x='Time', y='Acceleration', label='Acceleration')

    # Set labels and title
    plt.xlabel('Time')
    plt.ylabel('Magnitude')
    plt.title('Velocity and Acceleration')
    plt.xlim(0, max_tick)  # Adjust the x-axis limits
    plt.ylim(-30, 30)
    plt.legend()

    # Save the plot to the unique folder
    output_file = os.path.join(output_folder, 'tick_{}.png'.format(tick))
    plt.savefig(output_file)

    # Handling GIF
    image = Image.open(output_file)

    # Convert the image to RGBA mode if it's not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Append the image to the list
    images.append(image)

    # Close the figure
    plt.close()

gif_path = output_folder + '//output.gif'
# Save the list of images as a GIF file
images[0].save(gif_path, save_all=True, append_images=images[1:], duration=200, loop=0)