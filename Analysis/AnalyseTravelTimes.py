# type: ignore
"""
A script to analyse the travel times of a simulation.
"""
import json
import os
from tkinter.filedialog import asksaveasfilename

# pylint: disable=wrong-import-position
if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.getcwd())
# pylint: enable=wrong-import-position


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MultipleLocator
from scipy import stats as st
from scipy.optimize import curve_fit

from Analysis.OpenSimulation import open_simulation


def plot_travel_times_histogram(data, stats, project_folder, simulation_settings):
    """
    Plot the travel times of a simulation.
    """
    data = data["Traveltime"].to_numpy()

    plt.figure(figsize=(10, 6))

    plt.hist(
        data,
        bins=stats["bins"],
        density=True,
        label="Simulation data",
        alpha=0.5,
        rwidth=0.9,
        color="b",
    )

    # Also plot a line for the average travel time
    plt.axvline(stats["mean_travel_time"], color="k", linewidth=1)
    plt.text(
        stats["mean_travel_time"] + 0.1,
        0.8 * plt.ylim()[1],
        f"Average travel time: {stats['mean_travel_time']:.2f} s",
    )

    # Also plot a line for the most common travel time
    plt.axvline(stats["most_common_travel_time"], color="k", linewidth=1)
    plt.text(
        stats["most_common_travel_time"] + 0.1,
        0.7 * plt.ylim()[1],
        f"Most common travel time: {stats['most_common_travel_time']:.2f} s",
    )

    # Also plot a line for the standard deviation
    plt.axvline(
        stats["mean_travel_time"] + stats["std_dev"],
        color="k",
        linestyle="dashed",
        linewidth=1,
    )
    plt.text(
        stats["mean_travel_time"] + stats["std_dev"] + 0.1,
        0.6 * plt.ylim()[1],
        f"Standard deviation: {stats['std_dev']:.2f} s",
    )
    plt.axvline(
        stats["mean_travel_time"] - stats["std_dev"],
        color="k",
        linestyle="dashed",
        linewidth=1,
    )

    # Fit some distributions to the data
    x = np.linspace(0, stats["max_travel_time"], 1000)

    # Fit the normal distribution to the histogram
    p = st.norm.pdf(x, loc=stats["mean_travel_time"], scale=stats["std_dev"])
    plt.plot(x, p, "r", lw=2, label="Fitted Normal Distribution")

    # # Fit a poisson distribution to the data
    # p = poisson.pmf(x, stats["mean_travel_time"])
    # plt.plot(x, p, "r", lw=2, label="Fitted Poisson Distribution")

    # # Fit a exponential distribution to the data
    # loc, scale = expon.fit(data)
    # p = expon.pdf(x, loc, scale)
    # plt.plot(x, p, "r", label="Fitted Exponential")

    # # Fit a lognormal distribution to the data
    # shape, loc, scale = lognorm.fit(data)
    # p = lognorm.pdf(x, shape, loc, scale)
    # plt.plot(x, p, "y", label="Fitted Lognormal")

    # Set the limits of the plot
    grid_x_size = 5
    data_range = stats["max_travel_time"] - stats["min_travel_time"]
    min_x = divmod(stats["min_travel_time"] - data_range * 0.1, grid_x_size)[0] * grid_x_size
    max_x = (divmod(stats["max_travel_time"] + data_range * 0.1, grid_x_size)[0] + 1) * grid_x_size
    plt.gca().set_xlim([min_x, max_x])
    plt.gca().set_ylim([0, plt.gca().get_ylim()[1] * 1.1])

    plt.legend(fancybox=True, framealpha=1, shadow=True, borderpad=1)

    # Configure the grid
    plt.grid(which="both", axis="both")
    # Change major ticks to show every 20.
    plt.gca().xaxis.set_major_locator(MultipleLocator(5))
    # plt.gca().yaxis.set_major_locator(MultipleLocator(0.1))

    # Change minor ticks to show every 5. (20/4 = 5)
    plt.gca().xaxis.set_minor_locator(MultipleLocator(1))
    # plt.gca().yaxis.set_minor_locator(MultipleLocator(0.01))

    # Turn grid on for both major and minor ticks and style minor slightly
    # differently.
    plt.gca().grid(which="major", color="#CCCCCC", linestyle="--")
    plt.gca().grid(which="minor", color="#CCCCCC", linestyle=":")

    # Plot title
    behavior = simulation_settings["vehicle"]["behavior"][0]
    plt.title(f"Travel times {behavior}", fontsize=20)
    plt.xlabel("Travel time (s)", fontsize=15)
    plt.ylabel("Probability density", fontsize=15)

    # Tkinter to ask for a file name
    file = asksaveasfilename(
        title="Save vehicle data",
        filetypes=[("PNG", "*.png")],
        defaultextension=".png",
        initialdir=project_folder,
        initialfile="travel_times_histogram.png",
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

    # Show the plot
    plt.show()


def plot_travel_times_graph(data, stats, project_folder, simulation_settings):
    """
    Plot the travel times of a simulation.
    """
    time = data["Time"].to_numpy()
    data = data["Traveltime"].to_numpy()

    # Insert a 0 at the start of the data
    time = np.insert(time, 0, 0)
    data = np.insert(data, 0, 0)

    plt.figure(figsize=(10, 6))

    sim_data = plt.plot(time, data, label="Simulation data", alpha=0.5)

    # Also plot a line for the average travel time
    mean_travel_time = plt.hlines(
        stats["mean_travel_time"],
        time[0],
        time[-1],
        linestyle="solid",
        linewidth=1,
        label="Average travel time",
    )

    # Also plot a line for the most common travel time
    most_common = plt.hlines(
        stats["most_common_travel_time"],
        time[0],
        time[-1],
        linestyle=(0, (5, 10)),
        linewidth=1,
        label="Most common travel time",
    )

    # Also plot a line for the standard deviation
    std_dev_plus = plt.hlines(
        stats["mean_travel_time"] + stats["std_dev"],
        time[0],
        time[-1],
        color="k",
        linestyle="dashed",
        linewidth=1,
        label="Standard deviation",
    )
    std_dev_min = plt.hlines(
        stats["mean_travel_time"] - stats["std_dev"],
        time[0],
        time[-1],
        color=std_dev_plus.get_color(),
        linestyle="dashed",
        linewidth=1,
    )

    # Set the limits of the plot
    plt.gca().set_xlim([time[0], time[-1]])
    plt.gca().set_ylim([0, plt.gca().get_ylim()[1] * 1.1])

    plt.legend(fancybox=True, framealpha=1, shadow=True, borderpad=1)

    # Configure the grid
    plt.grid(which="both", axis="both")

    # Turn grid on for both major and minor ticks and style minor slightly
    # differently.
    plt.gca().grid(which="major", color="#CCCCCC", linestyle="--")
    plt.gca().grid(which="minor", color="#CCCCCC", linestyle=":")

    # Plot title
    behavior = simulation_settings["vehicle"]["behavior"][0]
    plt.title(f"Travel times {behavior}", fontsize=20)
    plt.xlabel("Time (s)", fontsize=15)
    plt.ylabel("Travel Times (s)", fontsize=15)

    # Tkinter to ask for a file name
    file = asksaveasfilename(
        title="Save vehicle data",
        filetypes=[("PNG", "*.png")],
        defaultextension=".png",
        initialdir=project_folder,
        initialfile="travel_times_plot.png",
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

    # Show the plot
    plt.show()

    # Now do the same but average the data over 10 seconds

    bin_size = 1000 * simulation_settings["simulation"]["time_step"]
    bins = np.arange(0, time.max() + bin_size, bin_size)
    travel_times_average = []

    for bin in bins:
        average = np.mean(data[(time >= bin) & (time < bin + bin_size)])
        travel_times_average.append(average)

    plt.figure(figsize=(10, 6))

    plt.plot(bins, travel_times_average, label="Simulation data", alpha=0.5)

    # Also plot a line for the average travel time
    plt.hlines(
        stats["mean_travel_time"],
        time[0],
        time[-1],
        linestyle="solid",
        linewidth=1,
        label="Average travel time",
    )

    # Also plot a line for the most common travel time
    plt.hlines(
        stats["most_common_travel_time"],
        time[0],
        time[-1],
        linestyle=(0, (5, 10)),
        linewidth=1,
        label="Most common travel time",
    )

    # Also plot a line for the standard deviation
    plt.hlines(
        stats["mean_travel_time"] + stats["std_dev"],
        time[0],
        time[-1],
        color="k",
        linestyle="dashed",
        linewidth=1,
        label="Standard deviation",
    )
    plt.hlines(
        stats["mean_travel_time"] - stats["std_dev"],
        time[0],
        time[-1],
        color="k",
        linestyle="dashed",
        linewidth=1,
    )

    # Set the limits of the plot
    plt.gca().set_xlim([time[0], time[-1]])
    plt.gca().set_ylim([0, plt.gca().get_ylim()[1] * 1.1])

    plt.legend(fancybox=True, framealpha=1, shadow=True, borderpad=1)

    # Configure the grid
    plt.grid(which="both", axis="both")
    # Change major ticks to show every 20.
    # plt.gca().xaxis.set_major_locator(MultipleLocator(50))
    # plt.gca().yaxis.set_major_locator(MultipleLocator(0.1))

    # Change minor ticks to show every 5. (20/4 = 5)
    # plt.gca().xaxis.set_minor_locator(MultipleLocator(5))
    # plt.gca().yaxis.set_minor_locator(MultipleLocator(0.01))

    # Turn grid on for both major and minor ticks and style minor slightly
    # differently.
    plt.gca().grid(which="major", color="#CCCCCC", linestyle="--")
    plt.gca().grid(which="minor", color="#CCCCCC", linestyle=":")

    # Plot title
    behavior = simulation_settings["vehicle"]["behavior"][0]
    plt.title(f"Travel times {behavior}", fontsize=20)
    plt.xlabel("Time (s)", fontsize=15)
    plt.ylabel("Travel Times (s)", fontsize=15)

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

    # Show the plot
    plt.show()


def get_stats(data, simulation_settings):
    """
    Get the stats of the data.
    """
    travel_times = data["Traveltime"].to_numpy()
    stats = dict()
    stats["min_travel_time"] = np.min(travel_times)
    stats["max_travel_time"] = np.max(travel_times)
    stats["mean_travel_time"] = np.mean(travel_times)
    stats["std_dev"] = np.std(travel_times)

    bins = np.arange(
        stats["min_travel_time"],
        stats["max_travel_time"],
        (stats["max_travel_time"] - stats["min_travel_time"]) / 50,
    )
    hist, bins = np.histogram(travel_times, bins=bins)

    stats["most_common_travel_time"] = bins[np.argmax(hist)]
    stats["amount_of_most_common_travel_time"] = np.argmax(travel_times)
    # stats["real_time"] = simulation_time_data["real_time"]
    # stats["simulation_time"] = simulation_time_data["simulation_time"]
    stats["amount_of_cars"] = len(travel_times)
    # stats["road_length"] = road.length
    # stats["num_of_lanes"] = road.num_of_lanes
    stats["bins"] = bins
    stats["goodness_of_fit"], stats["best_fit"] = run_kolmogorov_smirnov_test(data)
    return stats


def save_stats(folder, stats) -> None:
    """
    Print stats using the stats dictionary make sure they are aligned
    """
    stat_strings = []
    stat_strings.append(
        f"Minimum travel time: \t{stats['min_travel_time']:.2f} s or {stats['min_travel_time'] / 60:.2f} min"
    )
    stat_strings.append(
        f"Maximum travel time: \t{stats['max_travel_time']:.2f} s or {stats['max_travel_time'] / 60:.2f} min"
    )
    stat_strings.append(
        f"Average travel time: \t{stats['mean_travel_time']:.2f} s or {stats['mean_travel_time'] / 60:.2f} min"
    )
    stat_strings.append(
        f"Most common time: \t{stats['most_common_travel_time']:.2f} s or {stats['most_common_travel_time'] / 60:.2f} min"
    )
    stat_strings.append(
        f"# of most common time: \t{stats['amount_of_most_common_travel_time']} / {stats['amount_of_cars']} ({stats['amount_of_most_common_travel_time'] / stats['amount_of_cars'] * 100:.2f}%))"
    )
    stat_strings.append(f"Standard deviation: \t{stats['std_dev']:.2f} s")
    stat_strings.append(f"Amount of cars: \t{stats['amount_of_cars']}")
    stat_strings.append(f"Best fit: \t\t{stats['best_fit']}")
    # Use json.dumps to make sure the data is aligned
    goodnes_of_fit_json = json.dumps(stats["goodness_of_fit"], indent=4)
    stat_strings.append(f"Goodness of fit: \t{goodnes_of_fit_json}")

    path = os.path.join(folder, "stats.txt")
    with open(path, "w", encoding="utf-8") as file:
        for stat in stat_strings:
            file.write(stat + "\n")
            print(stat)


def run_kolmogorov_smirnov_test(data):
    """
    Run the Kolmogorov-Smirnov test on the data.
    """

    def is_discrete(dist):
        if hasattr(dist, "dist"):
            return isinstance(dist.dist, st.rv_discrete)
        else:
            return isinstance(dist, st.rv_discrete)

    travel_times = data["Traveltime"].to_numpy()

    continuous_distributions = {
        "norm": [],
        "expon": [],
        "lognorm": [],
        "gamma": [],
        "beta": [],
        "uniform": [],
        "triang": [],
        "weibull_min": [],
        "weibull_max": [],
        "pareto": [],
        "genextreme": [],
    }
    for dist_name in continuous_distributions:
        params = {}
        dist = getattr(st, dist_name)
        param = dist.fit(travel_times)

        params[dist_name] = param
        # Applying the Kolmogorov-Smirnov test
        ks_statistic, p_value = st.kstest(travel_times, dist_name, args=param)
        continuous_distributions[dist_name] = {
            "parameters": param,
            "ks_statistic": ks_statistic,
            "p_value": p_value,
        }
    best_fit = min(
        continuous_distributions,
        key=lambda x: continuous_distributions[x]["ks_statistic"],
    )
    return continuous_distributions, best_fit


def analyse_travel_times() -> None:
    """
    Analyse the travel times of a simulation.
    """
    ##################################

    print("Opening simulation...")

    path, project_folder, simulation_settings = open_simulation(preference_file="travel_times.csv")

    ##################################

    print("Reading data...")

    # Read the data from the file, ignore the first row which is a header
    data = pd.read_csv(path, header=0)
    # Specify the column types
    data = data.astype(
        {
            "Time": float,
            "Traveltime": float,
        }
    )

    # Check if data is empty if so raise an error
    if len(data) == 0:
        raise ValueError(f"Data {data} is empty.")

    print(data)
    stats = get_stats(data, simulation_settings)
    save_stats(project_folder, stats)
    plot_travel_times_histogram(data, stats, project_folder, simulation_settings)
    plot_travel_times_graph(data, stats, project_folder, simulation_settings)


if __name__ == "__main__":
    analyse_travel_times()
