from tkinter import *
from Animations.AnimateVehiclePyGame import show_animation
from simulation_3 import simulate
from Analysis.AnalyseTravelTimes import analyse_travel_times
from Analysis.AnalyseVehicleData import analyse_vehicle_data
from tkinter import messagebox
import traceback
from GUI.simulation_settings import show_simulation_settings_gui


class MainApplication:
    def run_simulation(self):
        self.root.withdraw()
        try:
            simulate()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            traceback.print_exc()
        self.root.deiconify()

    def show_animation_gui(self):
        self.root.withdraw()
        try:
            show_animation()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            traceback.print_exc()
        self.root.deiconify()

    def analyse_travel_times_gui(self):
        self.root.withdraw()
        try:
            analyse_travel_times()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            traceback.print_exc()
        self.root.deiconify()

    def analyse_vehicle_data_gui(self):
        self.root.withdraw()
        try:
            analyse_vehicle_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            traceback.print_exc()
        self.root.deiconify()

    def __init__(self) -> None:
        self.root = Tk()

        self.root.title("Traffic Simulation")

        simulation_labelframe = LabelFrame(self.root, text="Simulation")
        simulation_labelframe.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        simulation_button = Button(
            simulation_labelframe,
            text="Run Simulation",
            command=self.run_simulation,
            padx=10,
            pady=10,
        )
        simulation_button.pack(padx=10, pady=10)

        animation_button = Button(
            simulation_labelframe,
            text="Show Simulation",
            command=self.show_animation_gui,
            padx=10,
            pady=10,
        )
        animation_button.pack(padx=10, pady=10)

        analysis_labelframe = LabelFrame(self.root, text="Analysis")
        analysis_labelframe.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        travel_times_button = Button(
            analysis_labelframe,
            text="Analyse Travel Times",
            command=self.analyse_travel_times_gui,
            padx=10,
            pady=10,
        )
        travel_times_button.pack(padx=10, pady=10)

        vehicle_data_button = Button(
            analysis_labelframe,
            text="Analyse Vehicle Data",
            command=self.analyse_vehicle_data_gui,
            padx=10,
            pady=10,
        )
        vehicle_data_button.pack(padx=10, pady=10)

        project_settings_button = Button(
            analysis_labelframe,
            text="Show simulation Settings",
            command=show_simulation_settings_gui,
            padx=10,
            pady=10,
        )
        project_settings_button.pack(padx=10, pady=10)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def mainloop(self):
        self.root.mainloop()
