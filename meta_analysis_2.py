# type: ignore
import os
from tkinter.filedialog import askdirectory

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from Analysis.AnalyseTravelTimes import analyse_travel_times
from run_multiple import open_simulation

# Ask for folder
tmpfolder = askdirectory(title="Select folder with simulation results", initialdir=os.getcwd())

runtimes = {}

folder_list = [f.path for f in os.scandir(tmpfolder) if f.is_dir()]
for folder in tqdm(folder_list):
    _, _, simulation_settings = open_simulation(
        preference_file="simulation_settings.json", folder=folder
    )
    behavior = simulation_settings["vehicle"]["behavior"][0]
    cars_per_second = simulation_settings["spawn"]["cars_per_second"]
    duration = simulation_settings["process"]["runtime"]
    if behavior not in runtimes:
        runtimes[behavior] = {}
    runtimes[behavior][cars_per_second] = duration

# Create a new list with the cars per second values
cps = []
for behavior in runtimes:
    for cars_per_second in runtimes[behavior]:
        cps.append(cars_per_second)
cps = list(set(cps))
cps.sort()

# Create a list per behavior for the durations
# If a behavior does not have a duration for a certain cars per second value, add None
durations = {}
for behavior in runtimes:
    durations[behavior] = []
    for cars_per_second in cps:
        if cars_per_second in runtimes[behavior]:
            durations[behavior].append(runtimes[behavior][cars_per_second])
        else:
            durations[behavior].append(None)

for cars_per_second in cps:
    print(f"{cars_per_second} cars per second:")
    for behavior in durations:
        print(f"\t{behavior}: {durations[behavior][cps.index(cars_per_second)]}")

# Plot the results
plt.figure(figsize=(10, 5))
plt.title("Runtime of the simulations")
plt.xlabel("Cars per second")
plt.ylabel("Runtime (s)")
for behavior in durations:
    plt.plot(cps, durations[behavior], label=behavior)
plt.legend()
plt.grid()
plt.xlim(left=0, right=max(cps))
plt.ylim(bottom=0)
plt.xticks(np.arange(0, max(cps) + 0.1, 0.1))
plt.savefig(os.path.join(tmpfolder, "runtimes.png"))
plt.show()
