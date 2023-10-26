import os
import traceback as tb
import time
import json


class DataCollector:
    def __init__(self, simulation_id: str):
        self.vehicle_data = []
        self.travel_times = []

        self.car_data = {}

        self.simulation_id = simulation_id

        self.iteration = 0
        self.maximum_data = 3 * 1e6

        self.current_simulation_time = None

    def __enter__(self):
        self.path = self.create_folder(self.simulation_id)
        self.write_header(self.path)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.export_data()
        if exc_type is not None:
            print(exc_type, exc_value)
            tb.print_tb(traceback)
            raise exc_type(exc_value)

    def create_folder(self, simulation_id: str):
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
        else:
            # If folder exists, check if there are files in the folder
            files = os.listdir(path)
            if len(files) == 0:
                return path
            else:
                # Add a number to the folder name
                folder_number = 2
                path = os.path.join(
                    os.getcwd(), "tmp", f"{simulation_id}_{folder_number}"
                )
                while os.path.exists(path):
                    folder_number += 1
                    path = os.path.join(
                        os.getcwd(), "tmp", f"{simulation_id}_{folder_number}"
                    )
                os.mkdir(path=path)
                return path

    def collect_data(self, vehicle, lane_index=None):
        # Collect data for each vehicle (e.g., position, velocity)
        # ToDo: Kijken naar verdwijnende auto's
        self.iteration += 1

        self.vehicle_data.append(
            [
                self.current_simulation_time,
                vehicle.id,
                lane_index,
                vehicle.position,
                vehicle.velocity,
            ]
        )

        if self.iteration >= self.maximum_data:
            print(f"Maximum reached: {self.iteration} / {self.maximum_data}")
            start = time.perf_counter_ns()
            self.export_data()
            self.iteration = 0
            print(f"{(time.perf_counter_ns() - start) / 1e9} s")

    def add_new_simulation_time(self, simulation_time):
        # Add a new simulation time
        self.current_simulation_time = simulation_time

    def vehicle_added(self, vehicle, simulation_time):
        # Record the time when a vehicle is added to the road
        self.car_data[vehicle.id] = {"start_time": simulation_time}

    def vehicle_deleted(self, vehicle, simulation_time):
        # Calculate and record the travel time of a vehicle
        self.car_data[vehicle.id]["stop_time"] = simulation_time
        self.car_data[vehicle.id]["travel_time"] = (
            simulation_time - self.car_data[vehicle.id]["start_time"]
        )
        self.travel_times.append(self.car_data[vehicle.id]["travel_time"])

    def write_data(self):
        # Write data to a file
        vehicle_file = os.path.join(self.path, "vehicle_data.csv")
        with open(vehicle_file, "a") as f:
            # Write data rows
            for vehicle_data in self.vehicle_data:
                f.write(",".join([str(data) for data in vehicle_data]) + "\n")

        travel_time_file = os.path.join(self.path, "travel_times.csv")
        with open(travel_time_file, "a") as f:
            # Write travel times
            for travel_time in self.travel_times:
                f.write(f"{travel_time}\n")

    def write_header(self, filename):
        # Export collected data to a file (e.g., CSV)

        vehicle_file = os.path.join(self.path, "vehicle_data.csv")
        with open(vehicle_file, "w") as f:
            # Write header row
            self.current_simulation_time,
            f.write("time,vehicle_id,lane_index,position,velocity\n")

        travel_time_file = os.path.join(self.path, "travel_times.csv")
        with open(travel_time_file, "w") as f:
            # Write travel times
            f.write("Travel Times\n")

    def export_data(self):
        # Export collected data to a file (e.g., CSV)
        self.write_data()
        self.vehicle_data = []
        self.travel_times = []

    def add_extra_data(self, data: dict):
        # Save data as json to a file
        filename = os.path.join(self.path, "simulation_settings.json")
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
