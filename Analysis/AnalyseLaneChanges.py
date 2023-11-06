# type: ignore
"""
Analyse the lane changes of a simulation.
"""
import colorsys
import os
from tkinter.filedialog import askdirectory, asksaveasfilename
from typing import Any

import matplotlib.colors as mc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from Analysis.OpenSimulation import open_simulation


def analyse_lane_changes(
    show: bool, ask_save: bool, simulations: list[tuple[str, str, dict[str, Any]]] | None
):
    """
    Analyse the data from the simulations provided in the list.
    If no list is given, ask for a folder with simulation results.
    Plots the data in two graphs:
    - Amount of lane changes over time of the different simulations in the list
    - Average amount of lane changes over time of the different simulations in the list
    Also saves the graphs as a png file.
    """

    if simulations is None:
        print("Opening simulation...")

        folder = askdirectory(title="Select folder with simulation results", initialdir=os.getcwd())

        simulations = []
        folder_list = [f.path for f in os.scandir(folder) if f.is_dir()]
        for folder in folder_list:
            simulations.append(open_simulation(preference_file="vehicle_data.csv"))

    ##################################

    print("Reading data...")

    # Read the data from the file, ignore the first row which is a header

    data = {}
    for simulation in simulations:
        data[simulation[1]] = pd.read_csv(simulation[0], header=0)

        # Check if data is empty if so raise an error
        if len(data[simulation[1]]) == 0:
            raise ValueError(f"Data {data[simulation[1]]} is empty.")

    ##################################

    print("Analysing data...")

    # First create a list with the unique time values
    time_values = []
    for simulation in simulations:
        time_values.append(data[simulation[1]]["time"].unique())
    time_values = list(set(np.concatenate(time_values)))

    # Create a list per simulation for the lane changes
    # If a simulation does not have a lane change for a certain time value, add None
    lane_changes = create_lane_change_dataframe(time_values, data)

    # Calculate the average amount of lane changes per time step
    average_lane_changes = get_average_lane_changes(lane_changes)

    ##################################

    print("Plotting results...")

    plot_lane_change_results(show, ask_save, time_values, lane_changes, average_lane_changes)


def create_lane_change_dataframe(
    time_values: list, data: dict[str, pd.DataFrame]
) -> dict[str, list]:
    """
    Create a column to the data with the lane change of the vehicle.
    """
    # Create a list per simulation for the lane changes
    # If a simulation does not have a lane change for a certain time value, add None
    lane_changes = {}
    for simulation in data:
        lane_changes[simulation[1]] = return_lane_changes_list(time_values, data[simulation])

    return lane_changes


def return_lane_changes_list(time_values: list, data: pd.DataFrame) -> list:
    """
    Create a column to the data with the lane change of the vehicle.
    """
    # Create a list per simulation for the lane changes
    # If a simulation does not have a lane change for a certain time value, add None
    lane_changes = []
    for i, time_value in enumerate(time_values):
        if not (time_value in data["time"].values):
            # If the time value is not in the data, add None
            lane_changes.append(None)
            continue

        # Amount of lane changes is the amount of vehicles that changed lanes in the last time step
        # If a vehicle is not present at the last time step, it is not counted as a lane change

        lane_changes_per_time_step = 0
        for vehicle in data[data["time"] == time_value]["vehicle_id"].values:
            # Check if the vehicle was present in the previous time step
            if not vehicle in data[data["time"] == time_values[i - 1]]["vehicle_id"].values:
                continue

            # Check if the vehicle changed lanes
            if not (
                data[(data["time"] == time_value) & (data["vehicle_id"] == vehicle)][
                    "lane_index"
                ].values[0]
                == data[(data["time"] == time_values[i - 1]) & (data["vehicle_id"] == vehicle)][
                    "lane_index"
                ].values[0]
            ):
                lane_changes_per_time_step += 1

    return lane_changes


def get_average_lane_changes(lane_changes: dict[str, list]) -> dict[str, float]:
    """
    Calculate the average amount of lane changes per time step.
    """
    average_lane_changes = {}
    for simulation in lane_changes:
        average_lane_changes[simulation] = np.mean(lane_changes[simulation])
    return average_lane_changes


def plot_lane_change_results(
    show: bool,
    ask_save: bool,
    time: list[float],
    lane_changes: dict[str, list],
    average_lane_changes: dict[str, float],
):
    """
    Plot the results.
    """
    # Create a figure with 3 subplots in a column
    fig = plt.figure(figsize=(10, 5))

    # Create a line plot of the lane changes
    for simulation in lane_changes:
        plt.plot(time, lane_changes[simulation], label=simulation)

    # Create a line plot of the average lane changes
    for simulation in average_lane_changes:
        plt.plot(
            time,
            [average_lane_changes[simulation]] * len(time),
            label=f"{simulation} average",
            linestyle="dashed",
        )

    # Create a legend
    plt.legend()

    # Create labels
    plt.xlabel("Time (s)")
    plt.ylabel("Amount of lane changes")

    # Ask for a filename to save the figure
    if ask_save:
        filename = asksaveasfilename(
            title="Save figure as",
            initialdir=os.getcwd(),
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )
        fig.savefig(
            filename,
            dpi=300,
            format="png",
            bbox_inches="tight",
            transparent=False,
        )

    # Show the figure
    if show:
        plt.show()
