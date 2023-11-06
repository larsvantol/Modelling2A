# type: ignore
"""
A script to analyse the vehicle data of a simulation.
"""
from tkinter.filedialog import asksaveasfilename
from tkinter.simpledialog import askinteger
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import tqdm

from Analysis.OpenSimulation import open_simulation


def analyse_vehicle_data(
    show: bool,
    ask_save: bool,
    vehicle_id: None | int = None,
    data: pd.DataFrame | None = None,
    simulation: tuple[str, str, dict[str, Any]] | None = None,
) -> None:
    """
    Analyse the vehicle data of a simulation.
    """
    ##################################

    print("Opening simulation...")

    if simulation is None:
        path, project_folder, simulation_settings = open_simulation(
            preference_file="vehicle_data.csv",
        )
    else:
        path, project_folder, simulation_settings = simulation

    ##################################

    print("Reading data...")

    # Read the data from the file, ignore the first row which is a header
    if data is None:
        data = pd.read_csv(path, header=0)

    # Check if data is empty if so raise an error
    if len(data) == 0:
        raise ValueError(f"Data {data} is empty.")

    #################################

    vehicles_ids = data["vehicle_id"].unique()

    if vehicle_id is None:
        min_vehicle_id = min(vehicles_ids)
        max_vehicle_id = max(vehicles_ids)
        while not vehicle_id in data["vehicle_id"].values:
            vehicle_id = askinteger(
                "Vehicle ID",
                f"Enter the ID of the vehicle you want to analyse: \n [{min_vehicle_id} - {max_vehicle_id}]",
            )
    if not vehicle_id in data["vehicle_id"].values:
        raise ValueError(f"Vehicle ID {vehicle_id} does not exist.")

    print("Filtering data...")
    # filter data
    data = data[data["vehicle_id"] == vehicle_id]

    #################################

    delta_t = simulation_settings["simulation"]["time_step"]

    print("Calculating acceleration...")

    def calculate_acceleration(velocity, previous_velocity, time_step):
        return (velocity - previous_velocity) / time_step

    # add previous velocity to data
    data["previous_velocity"] = data["velocity"].shift(1)

    for row in tqdm.tqdm(data.iterrows(), total=len(data)):
        row = row[1]
        data.loc[row.name, "acceleration"] = calculate_acceleration(
            row["velocity"], row["previous_velocity"], delta_t
        )

    print(data)

    #################################

    # shift time steps to start at 0
    time_steps = data["time"].values
    time_steps -= time_steps[0]

    positions = data["position"].values
    velocities = data["velocity"].values
    accelerations = data["acceleration"].values
    lane_changes = data["lane_index"].values

    #################################

    print("Plotting data...")

    # Create a figure with 3 subplots in a column
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
    fig.tight_layout(pad=2.0)

    # Create a line plot of the positions
    ax1.plot(time_steps, positions, label="Position")
    ax1.axis(ymin=0 - 1 / 20)
    # Create a line plot of the velocities
    ax2.plot(time_steps, velocities, label="Velocity")
    ax2.axis(ymin=0 - 1 / 20, ymax=40)
    # Create a line plot of the accelerations
    ax3.plot(time_steps, accelerations, label="Acceleration")
    ax3.axis(ymin=-10, ymax=10)
    # Create a line plot of the lane changes
    ax4.plot(time_steps, lane_changes, label="Lane changes")
    # For lane changes, y axis should be positive
    ax4.axis(ymin=0 - 1 / 20, ymax=simulation_settings["road"]["lanes"] - 1)

    # Set the x axis to start at 0 and end at the last time step
    ax1.axis(xmin=0, xmax=time_steps[-1])
    ax2.axis(xmin=0, xmax=time_steps[-1])
    ax3.axis(xmin=0, xmax=time_steps[-1])
    ax4.axis(xmin=0, xmax=time_steps[-1])

    # Set the title of the figure
    fig.suptitle(f"Vehicle Data: {vehicle_id}")

    # Set the labels of the axes
    ax1.set_ylabel("Position (m)")
    ax1.yaxis.label.set_size(8)
    ax2.set_ylabel("Velocity (ms⁻¹)")
    ax2.yaxis.label.set_size(8)
    ax3.set_ylabel("Acceleration (ms⁻²)")
    ax3.yaxis.label.set_size(8)
    ax4.set_ylabel("Lane changes")
    ax4.yaxis.label.set_size(8)

    ax4.set_xlabel("Time (s)")

    # Show the legend
    # ax1.legend(loc="upper right", fancybox=True, framealpha=1, shadow=True, borderpad=1)
    # ax2.legend(loc="upper right", fancybox=True, framealpha=1, shadow=True, borderpad=1)
    # ax3.legend(loc="upper right", fancybox=True, framealpha=1, shadow=True, borderpad=1)
    # ax4.legend(loc="upper right", fancybox=True, framealpha=1, shadow=True, borderpad=1)

    # Tkinter to ask for a file name
    if ask_save:
        file = asksaveasfilename(
            title="Save vehicle data",
            filetypes=[("PNG", "*.png")],
            defaultextension=".png",
            initialdir=project_folder,
            initialfile=f"vehicle_data_{vehicle_id}.png",
        )
    else:
        file = f"{project_folder}/vehicle_data_{vehicle_id}.png"
    plt.savefig(
        file,
        dpi=300,
        format="png",
        bbox_inches="tight",
        transparent=False,
    )
    # plt.savefig(
    #     file.replace(".png", "_transparent.png"),
    #     dpi=300,
    #     format="png",
    #     bbox_inches="tight",
    #     transparent=True,
    # )

    # Show the plot
    if show:
        plt.show()

    #################################


if __name__ == "__main__":
    analyse_vehicle_data(show=True, ask_save=True)
