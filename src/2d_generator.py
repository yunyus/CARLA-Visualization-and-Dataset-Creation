import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import os
from PIL import Image
import matplotlib.patches as patches
import math
import re

# For GIF
images = []

# Read the Excel file
data = pd.read_excel('zo/data.xlsx')

# Create a unique folder for each run
output_folder = 'zootput' + str(time.time())
os.makedirs(output_folder, exist_ok=True)

walker_proxy = plt.Line2D([], [], linestyle='None', marker='o', color='blue')
vehicle_proxy = plt.Line2D([], [], linestyle='None', marker='s', color='red')
cross_proxy = plt.Line2D([], [], linestyle='dashed', marker='o', color='grey')

# Iterate over each tick value
for tick in data['Tick'].unique():

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Line 1
    # Define the side border lines of the crosswalk
    border_lines = [
        (-9, -215, -9, -187),
        (-16, -215, -16, -187)
    ]

    # Calculate the number of crosswalk lines needed
    height_difference = 2
    num_lines = int((abs(-215 - -185) + 1) / height_difference)

    # Calculate the y-coordinate values for the crosswalk lines
    y_coordinates = [-215 + i * height_difference for i in range(num_lines)]

    # Plot the crosswalk lines
    for y in y_coordinates:
        x1, x2 = -9, -16
        plt.plot([x1, x2], [y, y], linestyle='dashed', color='grey')

    # Line 2
    # Define the side border lines of the crosswalk
    border_lines = [
        (15, -215, 15, -185),
        (22, -215, 22, -185)
    ]

    # Plot the crosswalk lines
    for y in y_coordinates:
        x1, x2 = 15, 22
        plt.plot([x1, x2], [y, y], linestyle='dashed', color='grey')

    # Define the starting and target locations
    start_location = (-80, -195)
    target_location = (160, -195)

    # Plot the starting and target locations
    plt.plot(start_location[0], start_location[1], marker='D', color='green')
    plt.plot(target_location[0], target_location[1], marker='D', color='green')

    # Filter data for the current tick
    tick_data = data[data['Tick'] == tick]

    # Plot walkers as circles
    walkers = tick_data[tick_data['Type'] == 'Walker']
    ax.scatter(walkers['Location X'], walkers['Location Y'], c='blue', marker='o')

    # Plot vehicles as rectangles
    vehicles = tick_data[tick_data['Type'] == 'Vehicle']
    ax.scatter(vehicles['Location X'], vehicles['Location Y'], c='red', marker='s')

    for index, vehicle in vehicles.iterrows():

        spd = vehicle['Speed']
        direction_x = float(vehicle['Direction X'])
        direction_y = float(vehicle['Direction Y'])

        length = 0
        a = 0
        b = 0
        c = 0
        match = re.search(r'x=(-?\d+\.\d+), y=(-?\d+\.\d+), z=(-?\d+\.\d+)', spd)
        if match:
            a = float(match.group(1))
            b = float(match.group(2))
            c = float(match.group(3))
            length = math.sqrt(a ** 2 + b ** 2 + c ** 2)

        dx = a
        dy = b

        x = vehicle['Location X']
        y = vehicle['Location Y']

        arrow = patches.Arrow(x, y, dx, dy, width=0.8, color='black')
        ax.add_patch(arrow)

    # Set axis limits based on the data
    ax.set_xlim(-85, 165)
    ax.set_ylim(data['Location Y'].min(), data['Location Y'].max())

    # Set the plot limits
    plt.xlim(-85, 165)
    plt.ylim(-220, -180)
    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    fig.suptitle('2D Simulation Plot')
    ax.set_title('Tick: {}'.format(tick))

    # Add legend
    ax.legend(handles=[walker_proxy, vehicle_proxy, cross_proxy], labels=['Walker', 'Vehicle', 'Crosswalks'])
    plt.legend(handles=[walker_proxy, vehicle_proxy, cross_proxy], labels=['Walker', 'Vehicle', 'Crosswalks'],
               loc='upper right')

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

