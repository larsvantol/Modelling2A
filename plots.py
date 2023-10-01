import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm, poisson, expon, lognorm


def plot_travel_times(road, stats):
    # Plot the data of the simulation

    plt.figure(figsize=(10, 6))

    plt.hist(
        road.data,
        bins=stats["bins"],
        density=True,
        label="Simulation data",
        alpha=0.5,
        rwidth=0.9,
        color="b",
    )
    plt.title("Travel times")

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
    plt.plot(x, p, "g", lw=2, label="Fitted Normal Distribution")

    # Fit a poisson distribution to the data
    p = poisson.pmf(x, stats["mean_travel_time"])
    plt.plot(x, p, "b", lw=2, label="Fitted Poisson Distribution")

    # Fit a exponential distribution to the data
    loc, scale = expon.fit(road.data)
    p = expon.pdf(x, loc, scale)
    plt.plot(x, p, "r", label="Fitted Exponential")

    # Fit a lognormal distribution to the data
    shape, loc, scale = lognorm.fit(road.data)
    p = lognorm.pdf(x, shape, loc, scale)
    plt.plot(x, p, "y", label="Fitted Lognormal")

    plt.xlabel("Travel time (s)")
    plt.ylabel("Probability density")

    plt.legend()

    plt.show()
