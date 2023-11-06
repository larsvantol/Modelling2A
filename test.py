import os
import shutil
from tkinter.filedialog import askdirectory

tmpfolder = askdirectory(title="Select folder with simulation results", initialdir=os.getcwd())
folder_list = [f.path for f in os.scandir(tmpfolder) if f.is_dir()]

# Create a new folder for the results
newfolder = askdirectory(
    title="Select folder for the new simulation results", initialdir=os.getcwd()
)

for folder in folder_list:
    # Create folder with same name as the original folder in the new folder
    folder_name = os.path.basename(folder)
    new_subfolder = os.path.join(newfolder, folder_name)

    # Copy all files except the csv files
    files = [
        f.path for f in os.scandir(folder) if f.is_file() and f.name.startswith("vehicle_data_")
    ]
    for file in files:
        new_file = os.path.join(new_subfolder, os.path.basename(file))
        shutil.copy2(file, new_file)
