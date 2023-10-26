print("Importing modules...")

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from Analysis.OpenSimulation import open_simulation
from tqdm import tqdm
from functools import partial

##################################

print("Opening simulation...")

path, project_folder, SIMULATION_SETTINGS = open_simulation()

##################################

print("Reading data...")

# Read the data from the file, ignore the first row which is a header
data = pd.read_csv(path, header=0)

# Check if data is empty if so raise an error
if len(data) == 0:
    raise ValueError(f"Data {data} is empty.")

##################################

print("Creating first things...")

# Create a figure and axis
fig, ax = plt.subplots(figsize=(50, 10))

print("Setting the limits...")

# Set the limits for the x and y axes
max_position = max(data["position"]) + 10
ax.set_xlim(0, max_position)
ax.set_ylim(0, SIMULATION_SETTINGS["road"]["lanes"])

# Draw the road
for lane_index in range(SIMULATION_SETTINGS["road"]["lanes"] + 1):
    ax.hlines(
        y=lane_index,
        xmin=0,
        xmax=max_position,
        color="black",
        linestyle="dashed",
        linewidth=1,
    )

print("Creating the color map...")

# Create a dictionary to map vehicle IDs to unique colors
colors = plt.cm.jet(np.linspace(0, 1, len(data["vehicle_id"])))
np.random.shuffle(colors)
color_dict = {
    vehicle_id: color for vehicle_id, color in zip(data["vehicle_id"], colors)
}

# Create a dictionary to keep track of rectangles for each vehicle
rectangles = {}

CAR_LENGTH = 1.5  # m


# Function to update the animation
def update(frame, pbar):
    pbar.update(1)
    # print(frame)
    ax.clear()  # Clear the previous frame
    ax.set_xlim(0, max_position)
    ax.set_ylim(0, SIMULATION_SETTINGS["road"]["lanes"])

    # Draw the road
    for lane_index in range(SIMULATION_SETTINGS["road"]["lanes"] + 1):
        ax.hlines(
            y=lane_index,
            xmin=0,
            xmax=max_position,
            color="black",
            linestyle="dashed",
            linewidth=1,
        )

    frame_vehicle_data = data[data["time"] == frame]
    for _, vehicle_data in frame_vehicle_data.iterrows():
        vehicle_id = vehicle_data["vehicle_id"]

        x = vehicle_data["position"]
        y = vehicle_data["lane_index"] + 0.5  # + 0.5 to center the vehicle in the lane

        if vehicle_id not in rectangles:
            rect = plt.Rectangle(
                (x - CAR_LENGTH / 2, y - 0.25),
                CAR_LENGTH,
                0.5,
                color=color_dict[vehicle_id],
                alpha=0.7,
            )
            ax.add_patch(rect)
            rectangles[vehicle_id] = rect
        else:
            rectangles[vehicle_id].set_x(x - CAR_LENGTH / 2)
            rectangles[vehicle_id].set_y(y - 0.25)
            ax.add_patch(rectangles[vehicle_id])

    ax.set_xlabel("Position")
    ax.set_title(f"Vehicle Animation at {frame:.1f} s")


print("Creating animation...")

# Only use every 10th frame to speed up the animation rendering
# frames = np.unique(data["time"])[::10]
frames = np.unique(data["time"])
print(len(frames))
# frames = frames[frames <= 100]

# Create an animation
with tqdm(total=len(frames)) as pbar:
    ani = animation.FuncAnimation(
        fig, partial(update, pbar=pbar), frames=frames, repeat=False
    )
    # Remove the file extension and add the datetime and .html
    filename = "animation_" + time.strftime("%d%m-%H%M%S") + ".html"
    filepath = os.path.join(project_folder, filename)

    # Save the animation as an html file
    ani.save(filename=filepath, writer="html")

# open the file
os.startfile(os.path.abspath(filepath))
