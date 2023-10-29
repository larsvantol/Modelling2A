"""A function to open a simulation folder and return the path to the file and the folder and the simulation settings"""
import json
import os
from tkinter.filedialog import askdirectory, askopenfilename
from typing import Any


def open_simulation(preference_file: str | None = None) -> tuple[str, str, dict[str, Any]]:
    """Open a simulation file and return the path to the file
    and the folder and the simulation settings"""

    print("Selecting file...")

    # Show file open dialog
    folder = askdirectory(initialdir=os.path.join(os.getcwd(), "tmp"))
    if not folder:
        raise ValueError("No folder selected.")

    print("Opening simulation settings...")
    simulation_settings_file = os.path.join(folder, "simulation_settings.json")
    if not os.path.exists(simulation_settings_file):
        raise FileNotFoundError(f"File {simulation_settings_file} does not exist.")
    with open(simulation_settings_file, "r", encoding="utf-8") as file:
        simulation_settings = json.load(file)

    if preference_file:
        # Check if preference file exists
        preference_file_path = os.path.join(folder, preference_file)
        if os.path.exists(preference_file_path):
            print("Opening preference file...")
            return preference_file_path, folder, simulation_settings

    filename = askopenfilename(initialdir=folder)
    if not filename:
        raise FileNotFoundError("No file selected.")

    path = os.path.join(folder, filename)

    print("Opening file...")

    # Check if path exists if not raise an error
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} does not exist.")

    return path, folder, simulation_settings


if __name__ == "__main__":
    path_, folder_, simulation_settings_ = open_simulation()
    print(path_)
    print(simulation_settings_)
