# type: ignore
import json
import os
from typing import Any

from tqdm import tqdm

from Analysis.AnalyseRoadRush import analyse_road_rush
from Analysis.AnalyseTravelTimes import analyse_travel_times
from simulation import simulate


def open_simulation(preference_file: str, folder: str) -> tuple[str, str, dict[str, Any]]:
    """Open a simulation file and return the path to the file
    and the folder and the simulation settings"""

    print("Selecting file...")

    if not folder:
        raise ValueError("No folder selected.")

    print("Opening simulation settings...")
    simulation_settings_file = os.path.join(folder, "simulation_settings.json")
    if not os.path.exists(simulation_settings_file):
        raise FileNotFoundError(f"File {simulation_settings_file} does not exist.")
    with open(simulation_settings_file, "r", encoding="utf-8") as file:
        simulation_settings = json.load(file)

    preference_file_path = os.path.join(folder, preference_file)
    if not os.path.exists(preference_file_path):
        raise FileNotFoundError(f"File {preference_file_path} does not exist.")

    print("Opening preference file...")
    return preference_file_path, folder, simulation_settings


def return_simulations_array(length, lanes, duration, cars_per_second) -> list[dict[str, Any]]:
    simulations = [
        {
            "name": {
                "id": f"IDM_{lanes}_{cars_per_second}_{duration}",
                "description": "Simulation Description",
            },
            "road": {"length": length, "lanes": 3},
            "simulation": {"time_step": 0.1, "duration": duration},
            "spawn": {"process": "poisson", "cars_per_second": cars_per_second},
            "vehicle": {
                "behavior": [
                    "Intelligent Driver Model",
                    {
                        "time_headway": {"mu": 1.5, "sigma": 0.15},
                        "max_acceleration": {"mu": 2.0, "sigma": 0.2},
                        "comfortable_braking_deceleration": {"mu": 3.0, "sigma": 0.2},
                        "minimum_spacing": {"mu": 2.0, "sigma": 0.2},
                        "acceleration_exponent": {"mu": 4.0, "sigma": 0.2},
                    },
                ],
                "behavior_settings": [27.78, 2.78],
                "length": 1.5,
            },
            "lane_distribution": "Triangle / Linear",
        },
        # {
        #     "name": {
        #         "id": f"Gipps_{lanes}_{cars_per_second}_{duration}",
        #         "description": "Simulation Description",
        #     },
        #     "road": {"length": length, "lanes": 3},
        #     "simulation": {"time_step": 0.1, "duration": duration},
        #     "spawn": {"process": "poisson", "cars_per_second": cars_per_second},
        #     "vehicle": {
        #         "behavior": [
        #             "Gipps Model",
        #             {
        #                 "maximum_acceleration": {"mu": 2.0, "sigma": 0.2},
        #                 "maximum_deceleration": {"mu": 4.0, "sigma": 0.2},
        #                 "apparent_reaction_time": {"mu": 2.0, "sigma": 0.2},
        #                 "comfortable_distance": {"mu": 2.0, "sigma": 0.2},
        #             },
        #         ],
        #         "behavior_settings": [27.78, 2.78],
        #         "length": 1.5,
        #     },
        #     "lane_distribution": "Triangle / Linear",
        # },
        # {
        #     "name": {
        #         "id": f"Simple_Following_Extended_{lanes}_{cars_per_second}_{duration}",
        #         "description": "Simple Following Extended Model",
        #     },
        #     "road": {"length": length, "lanes": 3},
        #     "simulation": {"time_step": 0.1, "duration": duration},
        #     "spawn": {"process": "poisson", "cars_per_second": cars_per_second},
        #     "vehicle": {
        #         "behavior": [
        #             "Simple Following Extended Model",
        #             {
        #                 "update_velocity_deviation": {"mu": 0.28, "sigma": 0.02},
        #                 "save_time": {"mu": 2.0, "sigma": 0.2},
        #             },
        #         ],
        #         "behavior_settings": [27.78, 2.78],
        #         "length": 1.5,
        #     },
        #     "lane_distribution": "Triangle / Linear",
        # },
    ]
    return simulations


def run_multiple():
    LENGTH = 5000
    LANES = 3
    DURATION = 36000
    simulations = []

    for cars_per_second in [0.01]:
        simulations.extend(return_simulations_array(LENGTH, LANES, DURATION, cars_per_second))

    for simulation in tqdm(simulations):
        folder = simulate(simulation)
        analyse_travel_times(
            False, False, open_simulation(preference_file="travel_times.csv", folder=folder)
        )
        analyse_road_rush(
            False, False, open_simulation(preference_file="vehicle_data.csv", folder=folder)
        )


if __name__ == "__main__":
    run_multiple()
