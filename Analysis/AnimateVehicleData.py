print("Importing modules...")

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

print("Opening file...")

folder = "tmp/simplefollowing_model/"
filename = "simplefollowing_model_1_vehicle_data.csv"
# folder = "tmp/gipps_model/"
# filename = "gipps_model_2_vehicle_data.csv"
path = os.path.join(folder, filename)

# Check if path exists if not raise an error
if not os.path.exists(path):
    raise FileNotFoundError(f"File {path} does not exist.")

print("Reading data...")

# Read the data from the file, ignore the first row which is a header
data = pd.read_csv(path, header=0)

# Check if data is empty if so raise an error
if len(data) == 0:
    raise ValueError(f"Data {data} is empty.")

#################################3

print("Creating first things...")

# Create a figure and axis
fig, ax = plt.subplots()

print("Setting the limits...")

# Set the limits for the x and y axes
max_position = max(data["position"]) + 10
ax.set_xlim(0, max_position)
ax.set_ylim(0, 1)

print("Creating the color map...")

# Create a dictionary to map vehicle IDs to unique colors
colors = plt.cm.jet(np.linspace(0, 1, len(data["vehicle_id"])))
np.random.shuffle(colors)
color_dict = {
    vehicle_id: color for vehicle_id, color in zip(data["vehicle_id"], colors)
}

# Create a dictionary to keep track of rectangles for each vehicle
rectangles = {}

car_length = 3  # m


# Function to update the animation
def update(frame):
    print(frame)
    ax.clear()  # Clear the previous frame
    ax.set_xlim(0, max_position)
    ax.set_ylim(0, 1)

    frame_vehicle_data = data[data["time"] == frame]
    for _, vehicle_data in frame_vehicle_data.iterrows():
        vehicle_id = vehicle_data["vehicle_id"]

        x = vehicle_data["position"]
        y = 0.5  # Y-coordinate for the center of the box

        if vehicle_id not in rectangles:
            rect = plt.Rectangle(
                (x - car_length / 2, y - 0.25),
                car_length,
                0.5,
                color=color_dict[vehicle_id],
                alpha=0.7,
            )
            ax.add_patch(rect)
            rectangles[vehicle_id] = rect
        else:
            rectangles[vehicle_id].set_x(x - car_length / 2)
            rectangles[vehicle_id].set_y(y - 0.25)
            ax.add_patch(rectangles[vehicle_id])

    ax.set_xlabel("Position")
    ax.set_title(f"Vehicle Animation at {frame:.1f} s")


print("Creating animation...")

# Only use every 10th frame to speed up the animation rendering
frames = np.unique(data["time"])[::20]
print(len(frames))
# frames = frames[frames <= 100]

# Create an animation
ani = animation.FuncAnimation(fig, update, frames=frames, repeat=False)

# Display the animation
# plt.gca().axes.get_yaxis().set_visible(False)  # Hide the y-axis
# plt.show()

##########################################

# # Display the animation
# plt.show()

# Remove the file extension and add the datetime and .html
filename = filename.split(".")[0] + "_" + time.strftime("%d%m-%H%M%S") + ".html"
filepath = os.path.join(folder, filename)

# Save the animation as an html file
ani.save(filename=filepath, writer="html")

# open the file
os.startfile(os.path.abspath(filepath))
