# type: ignore
"""
Analyse the data from the Road Rush simulation.
"""
import colorsys
from tkinter.filedialog import asksaveasfilename

import matplotlib.colors as mc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from Analysis.OpenSimulation import open_simulation


def lighten_color(
    color: str | tuple[float, float, float], amount: float = 0.5
) -> tuple[float, float, float]:
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    c = color if isinstance(color, tuple) else mc.to_rgb(color)
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


def analyse_road_rush() -> None:
    """
    Analyse the data from the Road Rush simulation.
    Plots the data in two graphs:
    - Amount of cars per lane
    - Average amount of cars per lane
    Also saves the graphs as a png file.
    """
    print("Opening simulation...")

    path, project_folder, simulation_settings = open_simulation(preference_file="vehicle_data.csv")

    ##################################

    print("Reading data...")

    # Read the data from the file, ignore the first row which is a header
    data = pd.read_csv(path, header=0)

    # Check if data is empty if so raise an error
    if len(data) == 0:
        raise ValueError(f"Data {data} is empty.")

    ##################################

    print("Analysing data...")

    # Calculate the statistics
    time_steps = data["time"].unique()

    amount_of_cars_per_time = (
        data.pivot_table(index="time", columns="lane_index", values="vehicle_id", aggfunc="count")
        .fillna(0)
        .astype(int)
    )

    # If there are no cars in a lane, the lane must be added to the dataframe
    for lane in range(simulation_settings["road"]["lanes"]):
        if lane not in amount_of_cars_per_time.columns:
            amount_of_cars_per_time[lane] = 0

    ##################################

    # Calculate the average amount of cars per time step

    amount_of_cars_per_lane_average = amount_of_cars_per_time.mean(axis=0)

    # Fit a line to the amount of cars per lane

    line_of_best_fit = {}
    for lane in range(simulation_settings["road"]["lanes"]):
        line_of_best_fit[lane] = np.polyfit(
            time_steps,
            amount_of_cars_per_time[lane],
            deg=1,
        )

    ##################################

    print("Plotting data...")

    # Plot the data

    lanes = simulation_settings["road"]["lanes"]
    plt.figure(figsize=(10, 5))
    for lane in range(lanes):
        plot_lane = plt.plot(time_steps, amount_of_cars_per_time[lane], label=f"Lane {lane}")
        average_line = plt.hlines(
            amount_of_cars_per_lane_average[lane],
            xmin=0,
            xmax=time_steps.max(),
            color=lighten_color(plot_lane[0].get_color()),
            linestyle="dashed",
        )
        plt.plot(
            time_steps,
            np.polyval(line_of_best_fit[lane], time_steps),
            color=lighten_color(average_line.get_color()),
            linestyle="dotted",
        )
        average_marker = Line2D([0], [0], label="Average", color="black", linestyle="dashed")
    line_of_best_fit_marker = Line2D(
        [0], [0], label="Line of best fit", color="black", linestyle="dotted"
    )
    handles, _ = plt.gca().get_legend_handles_labels()
    handles.append(average_marker)
    handles.append(line_of_best_fit_marker)
    plt.ylabel("Amount of cars in lane")
    plt.grid(True)
    plt.gca().set_ylim(bottom=0)
    plt.gca().set_xlim(left=0, right=time_steps.max())
    plt.xlabel("Time (s)")
    plt.legend(handles=handles, fancybox=True, framealpha=1, shadow=True, borderpad=1)
    plt.title("Amount of cars per lane")

    # Tkinter to ask for a file name
    file = asksaveasfilename(
        title="Save vehicle data",
        filetypes=[("PNG", "*.png")],
        defaultextension=".png",
        initialdir=project_folder,
        initialfile="road_rush.png",
    )
    plt.savefig(
        file,
        dpi=300,
        format="png",
        bbox_inches="tight",
        transparent=False,
    )
    plt.savefig(
        file.replace(".png", "_transparent.png"),
        dpi=300,
        format="png",
        bbox_inches="tight",
        transparent=True,
    )
    plt.show()

    ##################################

    # Now do the same thing but use the average amount of cars per time step in bins of 100 times the time step
    # This is to smooth out the data a bit

    # Calculate the average amount of cars per time step in bins of 100 times the time step
    bin_size = 1000 * simulation_settings["simulation"]["time_step"]
    bins = np.arange(0, data["time"].max() + bin_size, bin_size)
    amount_of_cars_per_time_average = {}
    for lane in range(lanes):
        for bin in bins:  # pylint: disable=redefined-builtin
            amount_of_cars = amount_of_cars_per_time[lane][
                (amount_of_cars_per_time.index >= bin)
                & (amount_of_cars_per_time.index < bin + bin_size)
            ].mean()
            amount_of_cars_per_time_average.setdefault(lane, []).append(amount_of_cars)

    line_of_best_fit_averages = {}
    for lane in range(simulation_settings["road"]["lanes"]):
        line_of_best_fit_averages[lane] = np.polyfit(
            bins,
            amount_of_cars_per_time_average[lane],
            deg=1,
        )

    ##################################

    print("Plotting data...")
    # Plot the data

    lanes = simulation_settings["road"]["lanes"]
    plt.figure(figsize=(10, 5))
    for lane in range(lanes):
        plot_lane = plt.plot(
            bins,
            amount_of_cars_per_time_average[lane],
            label=f"Lane {lane}",
        )
        average_line = plt.hlines(
            amount_of_cars_per_lane_average[lane],
            xmin=0,
            xmax=time_steps.max(),
            color=lighten_color(plot_lane[0].get_color()),
            linestyle="dashed",
        )
        plt.plot(
            time_steps,
            np.polyval(line_of_best_fit[lane], time_steps),
            color=lighten_color(average_line.get_color()),
            linestyle="dotted",
        )
    average_marker = Line2D([0], [0], label="Average", color="black", linestyle="dashed")
    line_of_best_fit_marker = Line2D(
        [0], [0], label="Line of best fit", color="black", linestyle="dotted"
    )
    handles, _ = plt.gca().get_legend_handles_labels()
    handles.append(average_marker)
    handles.append(line_of_best_fit_marker)
    plt.ylabel("Avg. amount of cars in lane")
    plt.grid(True)
    plt.gca().set_ylim(bottom=0)
    plt.gca().set_xlim(left=0, right=time_steps.max())
    plt.xlabel("Time (s)")
    plt.legend(handles=handles, fancybox=True, framealpha=1, shadow=True, borderpad=1)
    plt.title("Average amount of cars per lane")
    plt.savefig(
        file.replace(".png", "_average.png"),
        dpi=300,
        format="png",
        bbox_inches="tight",
        transparent=False,
    )
    plt.savefig(
        file.replace(".png", "_average_transparent.png"),
        dpi=300,
        format="png",
        bbox_inches="tight",
        transparent=True,
    )
    plt.show()


if __name__ == "__main__":
    analyse_road_rush()
