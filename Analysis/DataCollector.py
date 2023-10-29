"""DataCollector for collecting data from the simulation."""
import json
import os
import time
import traceback as tb
from typing import Any

from Vehicles.Vehicle import Vehicle


class DataCollector:
    """Collect data from the simulation."""

    def __init__(self, simulation_id: str):
        self.vehicle_data: list[tuple[float, int, int | None, float, float]] = []
        self.travel_times: list[float] = []

        self.car_data: dict[int, dict[str, Any]] = {}

        self.simulation_id: str = simulation_id
        self.path: str = self.create_folder(self.simulation_id)

        self.iteration: int = 0
        self.maximum_data: int = 3 * 10**6

        self.current_simulation_time: float = 0

    def __enter__(self):
        self.write_header()

        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
        self.export_data()
        if exc_type is not None:
            print(exc_type, exc_value)
            tb.print_tb(traceback)
            raise exc_type(exc_value)

    def create_folder(self, simulation_id: str):
        """Create a folder to store the data in"""
        # Check if there is a tmp folder in the current directory
        if not os.path.exists(os.path.join(os.getcwd(), "tmp")):
            # If not create a tmp folder
            os.mkdir(os.path.join(os.getcwd(), "tmp"))

        path = os.path.join(os.getcwd(), "tmp", simulation_id)

        # Check if there is a folder with the simulation_id in the tmp folder
        if not os.path.exists(path):
            # If not create a folder with the simulation_id
            os.mkdir(path=path)
            return path

        # If folder exists, check if there are files in the folder
        files = os.listdir(path)
        if len(files) == 0:
            return path

        # Add a number to the folder name
        folder_number = 2
        path = os.path.join(os.getcwd(), "tmp", f"{simulation_id}_{folder_number}")
        while os.path.exists(path):
            folder_number += 1
            path = os.path.join(os.getcwd(), "tmp", f"{simulation_id}_{folder_number}")
        os.mkdir(path=path)
        return path

    def collect_data(self, vehicle: Vehicle, lane_index: int | None = None):
        """Collect data from the vehicle,
        if the maximum number of data points is reached, export the data to a file"""

        # ToDo: Kijken naar verdwijnende auto's, misschien als de data wordt weggeschreven? # pylint: disable=fixme
        self.iteration += 1

        self.vehicle_data.append(
            (
                self.current_simulation_time,
                vehicle.id,
                lane_index,
                vehicle.position,
                vehicle.velocity,
            )
        )

        if self.iteration >= self.maximum_data:
            print(f"Maximum reached: {self.iteration} / {self.maximum_data}")
            start = time.perf_counter_ns()
            self.export_data()
            self.iteration = 0
            print(f"{(time.perf_counter_ns() - start) / 1e9} s")

    def set_new_simulation_time(self, simulation_time: float) -> None:
        """Set a new simulation time"""

        self.current_simulation_time = simulation_time

    def vehicle_added(self, vehicle: Vehicle, simulation_time: float):
        """Record the time when a vehicle is added to the road"""

        self.car_data[vehicle.id] = {"start_time": simulation_time}

    def vehicle_deleted(self, vehicle: Vehicle, simulation_time: float):
        """Calculate and record the travel time of a vehicle"""

        self.car_data[vehicle.id]["stop_time"] = simulation_time
        self.car_data[vehicle.id]["travel_time"] = (
            simulation_time - self.car_data[vehicle.id]["start_time"]
        )
        self.travel_times.append(self.car_data[vehicle.id]["travel_time"])

    def write_data(self):
        """Write the collected data to a file"""

        vehicle_file = os.path.join(self.path, "vehicle_data.csv")
        with open(vehicle_file, "a", encoding="utf-8") as f:
            for vehicle_data in self.vehicle_data:
                f.write(",".join([str(data) for data in vehicle_data]) + "\n")

        travel_time_file = os.path.join(self.path, "travel_times.csv")
        with open(travel_time_file, "a", encoding="utf-8") as f:
            for travel_time in self.travel_times:
                f.write(f"{travel_time}\n")

    def write_header(self) -> None:
        """Write the header of the data files"""

        vehicle_file = os.path.join(self.path, "vehicle_data.csv")
        with open(vehicle_file, "w", encoding="utf-8") as f:
            f.write("time,vehicle_id,lane_index,position,velocity\n")

        travel_time_file = os.path.join(self.path, "travel_times.csv")
        with open(travel_time_file, "w", encoding="utf-8") as f:
            f.write("Travel Times\n")

    def export_data(self):
        """Export the collected data to a file (e.g., CSV)"""

        self.write_data()
        self.vehicle_data = []
        self.travel_times = []

    def add_extra_data(self, data: dict[str, Any]):
        """Add extra data to the simulation_settings.json file"""

        filename = os.path.join(self.path, "simulation_settings.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
