import os
from tkinter.filedialog import askdirectory

from Analysis.AnalyseLaneChanges import analyse_lane_changes
from run_multiple import open_simulation

# Ask for folder
tmpfolder = askdirectory(title="Select folder with simulation results", initialdir=os.getcwd())

# Filter the folder list to only include folders with _3_var_3600 in the name
p = 0.1
folder_list = [f.path for f in os.scandir(tmpfolder) if f.is_dir() and f"_3_{p}_3600" in f.path]
simulations = []
for folder in folder_list:
    simulations.append(open_simulation(preference_file="vehicle_data.csv", folder=folder))

analyse_lane_changes(False, True, simulations=simulations)
