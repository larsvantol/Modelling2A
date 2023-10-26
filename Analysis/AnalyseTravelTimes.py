import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MultipleLocator
from scipy.stats import norm
from tkinter.filedialog import asksaveasfilename
from Analysis.OpenSimulation import open_simulation


def plot_travel_times_histogram(data, stats, project_folder):
    # Plot the data of the simulation

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
    p = norm.pdf(x, loc=stats["mean_travel_time"], scale=stats["std_dev"])
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
    min_x = (
        divmod(stats["min_travel_time"] - data_range * 0.1, grid_x_size)[0]
        * grid_x_size
    )
    max_x = (
        divmod(stats["max_travel_time"] + data_range * 0.1, grid_x_size)[0] + 1
    ) * grid_x_size
    plt.gca().set_xlim([min_x, max_x])
    plt.gca().set_ylim([0, plt.gca().get_ylim()[1] * 1.1])

    plt.legend()

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
    plt.title("Travel times Gipps", fontsize=20)
    plt.xlabel("Travel time (s)", fontsize=15)
    plt.ylabel("Probability density", fontsize=15)

    # Tkinter to ask for a file name
    file = asksaveasfilename(
        title="Save vehicle data",
        filetypes=[("PNG", "*.png")],
        defaultextension=".png",
        initialdir=project_folder,
        initialfile=f"travel_times.png",
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


def get_stats(data):
    stats = dict()
    stats["min_travel_time"] = np.min(data)
    stats["max_travel_time"] = np.max(data)
    stats["mean_travel_time"] = np.mean(data)
    stats["std_dev"] = np.std(data)

    bins = np.arange(
        stats["min_travel_time"],
        stats["max_travel_time"],
        (stats["max_travel_time"] - stats["min_travel_time"]) / 50,
    )
    hist, bins = np.histogram(data, bins=bins)

    stats["most_common_travel_time"] = bins[np.argmax(hist)]
    stats["amount_of_most_common_travel_time"] = np.argmax(data)
    # stats["real_time"] = simulation_time_data["real_time"]
    # stats["simulation_time"] = simulation_time_data["simulation_time"]
    stats["amount_of_cars"] = len(data)
    # stats["road_length"] = road.length
    # stats["num_of_lanes"] = road.num_of_lanes
    stats["bins"] = bins
    return stats


def print_stats(stats):
    # Print stats using the stats dictionary make sure they are aligned
    print(
        f"Minimum travel time: \t{stats['min_travel_time']:.2f} s or {stats['min_travel_time'] / 60:.2f} min"
    )
    print(
        f"Maximum travel time: \t{stats['max_travel_time']:.2f} s or {stats['max_travel_time'] / 60:.2f} min"
    )
    print(
        f"Average travel time: \t{stats['mean_travel_time']:.2f} s or {stats['mean_travel_time'] / 60:.2f} min"
    )
    print(
        f"Most common time: \t{stats['most_common_travel_time']:.2f} s or {stats['most_common_travel_time'] / 60:.2f} min"
    )
    print(
        f"# of most common time: \t{stats['amount_of_most_common_travel_time']} / {stats['amount_of_cars']} ({stats['amount_of_most_common_travel_time'] / stats['amount_of_cars'] * 100:.2f}%))"
    )
    print(f"Standard deviation: \t{stats['std_dev']:.2f} s")
    print(f"Amount of cars: \t{stats['amount_of_cars']}")


def analyse_travel_times():
    ##################################

    print("Opening simulation...")

    path, project_folder, SIMULATION_SETTINGS = open_simulation(
        preference_file="travel_times.csv"
    )

    ##################################

    print("Reading data...")

    # Read the data from the file, ignore the first row which is a header
    data = pd.read_csv(path, header=None, skiprows=1).values.flatten()

    # Check if data is empty if so raise an error
    if len(data) == 0:
        raise ValueError(f"Data {data} is empty.")

    print(data)
    stats = get_stats(data)
    print_stats(stats)
    plot_travel_times_histogram(data, stats, project_folder)
