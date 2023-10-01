import os
import numpy as np
import pandas as pd

from PlotTravelTimes import plot_travel_times

# folder = "tmp/gipps_model/"
# filename = "gipps_model_1_travel_times.csv"
# folder = "tmp/simplefollowing_model/"
# filename = "simplefollowing_model_1_travel_times.csv"
folder = "tmp/simplefollowing_extended_model/"
filename = "simplefollowing_extended_model_1_travel_times.csv"
path = os.path.join(folder, filename)

# Check if path exists if not raise an error
if not os.path.exists(path):
    raise FileNotFoundError(f"File {path} does not exist.")

# Read the data from the file, ignore the first row which is a header
data = pd.read_csv(path, header=None, skiprows=1).values.flatten()

# Check if data is empty if so raise an error
if len(data) == 0:
    raise ValueError(f"Data {data} is empty.")


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


print(data)
stats = get_stats(data)
print_stats(stats)
plot_travel_times(data, stats)
