"""
This file contains the main window of the GUI.
"""
import traceback
from functools import partial
from tkinter import Tk, messagebox
from tkinter.ttk import Button, LabelFrame

from Analysis.AnalyseRoadRush import analyse_road_rush
from Analysis.AnalyseTravelTimes import analyse_travel_times
from Analysis.AnalyseVehicleData import analyse_vehicle_data
from Animations.AnimateVehiclePyGame import show_animation
from GUI.simulation_settings import show_simulation_settings
from simulation import simulate


class MainApplication:
    """
    The main window of the GUI.
    """

    def __init__(self) -> None:
        self.button_press_map = {
            "run_simulation": simulate,
            "show_animation": show_animation,
            "analyse_travel_times": analyse_travel_times,
            "analyse_vehicle_data": analyse_vehicle_data,
            "analyse_road_rush": analyse_road_rush,
            "show_simulation_settings": partial(show_simulation_settings, None),
        }

        self.root = self.create_window("Traffic Simulation")

        self.create_layout()

    def create_layout(self) -> None:
        """
        Create the buttons for the GUI.
        """

        simulation_labelframe = LabelFrame(self.root, text="Simulation")
        simulation_labelframe.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        simulation_button = Button(
            simulation_labelframe,
            text="Run Simulation",
            command=self.button_press_map["run_simulation"],
        )
        simulation_button.pack(padx=10, pady=10)

        animation_button = Button(
            simulation_labelframe,
            text="Show Simulation",
            command=self.button_press_map["show_animation"],
        )
        animation_button.pack(padx=10, pady=10)

        project_settings_button = Button(
            simulation_labelframe,
            text="Show simulation Settings",
            command=self.button_press_map["show_simulation_settings"],
        )
        project_settings_button.pack(padx=10, pady=10)

        analysis_labelframe = LabelFrame(self.root, text="Analysis")
        analysis_labelframe.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        travel_times_button = Button(
            analysis_labelframe,
            text="Analyse Travel Times",
            command=self.button_press_map["analyse_travel_times"],
        )
        travel_times_button.pack(padx=10, pady=10)

        vehicle_data_button = Button(
            analysis_labelframe,
            text="Analyse Vehicle Data",
            command=self.button_press_map["analyse_vehicle_data"],
        )
        vehicle_data_button.pack(padx=10, pady=10)

        road_rush_button = Button(
            analysis_labelframe,
            text="Analyse Road Rush",
            command=self.button_press_map["analyse_road_rush"],
        )
        road_rush_button.pack(padx=10, pady=10)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def create_window(self, title: str) -> Tk:
        """
        Create a new window.
        """
        window = Tk()
        window.title(title)
        return window

    def button_press(self, button_name: str) -> None:
        """
        Function that is binds the button press to the correct function.
        """
        if not button_name in self.button_press_map:
            raise ValueError(f"Button {button_name} does not exist.")

        self.root.withdraw()
        try:
            self.button_press_map[button_name]()
        except (
            Exception  # pylint: disable=broad-exception-caught
        ) as e:  # because we don't want to crash the GUI
            messagebox.showerror(title="Error", message=str(e))  # type: ignore
            traceback.print_exc()
        self.root.deiconify()

    def mainloop(self):
        """
        Start the main loop of the GUI.
        """
        self.root.mainloop()
