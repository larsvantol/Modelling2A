import os
from tkinter.filedialog import askdirectory

from Analysis.AnalyseTravelTimes import analyse_travel_times
from run_multiple import open_simulation

# Ask for folder
tmpfolder = askdirectory(title="Select folder with simulation results", initialdir=os.getcwd())

folder_list = [f.path for f in os.scandir(tmpfolder) if f.is_dir()]
for folder in folder_list:
    analyse_travel_times(
        False, False, open_simulation(preference_file="travel_times.csv", folder=folder)
    )
