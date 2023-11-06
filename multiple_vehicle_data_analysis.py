# type: ignore
import os
from tkinter.filedialog import askdirectory

import numpy as np
import pandas as pd
from tqdm import tqdm

from Analysis.AnalyseVehicleData import analyse_vehicle_data
from run_multiple import open_simulation

# Ask for folder
folder = askdirectory(
    title="Select folder with simulation results", initialdir=os.path.join(os.getcwd(), "tmp")
)
# analyse_travel_times(
#     False, False, open_simulation(preference_file="travel_times.csv", folder=folder)
# )

# dirslist = [f.path for f in os.scandir(foldertmp) if f.is_dir()]

# for folder in dirslist:
##################################

simulation = open_simulation(preference_file="vehicle_data.csv", folder=folder)

##################################

print("Reading data...")

# Read the data from the file, ignore the first row which is a header
data = pd.read_csv(simulation[0], header=0)
vehicles_ids = data["vehicle_id"].unique()

min_vehicle_id = min(vehicles_ids)
max_vehicle_id = max(vehicles_ids)

# Get 20 random vehicle ids
vehicle_ids = []
for _ in range(5):
    vehicle_id = np.random.randint(min_vehicle_id, max_vehicle_id)
    while not vehicle_id in data["vehicle_id"].values:
        vehicle_id = np.random.randint(min_vehicle_id, max_vehicle_id)
    vehicle_ids.append(vehicle_id)

for vehicle_id in tqdm(vehicle_ids):
    print(f"{folder}: Analysing vehicle {vehicle_id}...")
    analyse_vehicle_data(False, False, vehicle_id=vehicle_id, data=data, simulation=simulation)

##################################

print(f"Done! with {folder}")
