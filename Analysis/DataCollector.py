import os
import re
import time


class DataCollector:
    def __init__(self, folder, filename):
        self.vehicle_data = []
        self.travel_times = []

        self.car_data = {}

        self.path = self.create_filename(folder, filename)

        self.iteration = 0
        self.maximum_data = 3 * 1e6

        self.current_simulation_time = None

        self.write_header(self.path)

    def create_filename(self, folder, filename):
        # Create a folder to store the data files if the folder does not exist
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Check if a file with the same name already exists if so, increment the filename.
        i = 1
        original_filename = filename
        filename = f"{original_filename}_{i}"
        while len(
            [file for file in os.listdir(folder) if re.search(f"{filename}(.+)", file)]
        ):
            i += 1
            filename = f"{original_filename}_{i}"

        # Return the unique filename
        return os.path.join(folder, filename)

    def collect_data(self, vehicle):
        # Collect data for each vehicle (e.g., position, velocity)
        self.iteration += 1

        self.vehicle_data.append(
            [
                self.current_simulation_time,
                vehicle.id,
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

    def car_added(self, vehicle, simulation_time):
        # Record the time when a vehicle is added to the road
        self.car_data[vehicle.id] = {"start_time": simulation_time}

    def car_deleted(self, vehicle, simulation_time):
        # Calculate and record the travel time of a vehicle
        self.car_data[vehicle.id]["stop_time"] = simulation_time
        self.car_data[vehicle.id]["travel_time"] = (
            simulation_time - self.car_data[vehicle.id]["start_time"]
        )
        # print()
        # print(f"Vehicle {vehicle.id} has completed its journey.")
        # print(f"Start time: {self.car_data[vehicle.id]['start_time']}")
        # print(f"Stop time: {self.car_data[vehicle.id]['stop_time']}")
        # print(f"Travel time: {self.car_data[vehicle.id]['travel_time']}")
        self.travel_times.append(self.car_data[vehicle.id]["travel_time"])

    def write_data(self):
        # Write data to a file
        with open(f"{self.path}_vehicle_data.csv", "a") as f:
            # Write data rows
            for vehicle_data in self.vehicle_data:
                f.write(",".join([str(data) for data in vehicle_data]) + "\n")

        with open(f"{self.path}_travel_times.csv", "a") as f:
            # Write travel times
            for travel_time in self.travel_times:
                f.write(f"{travel_time}\n")

    def write_header(self, filename):
        # Export collected data to a file (e.g., CSV)

        with open(f"{self.path}_vehicle_data.csv", "w") as f:
            # Write header row
            f.write("time,vehicle_id,position,velocity\n")

        with open(f"{self.path}_travel_times.csv", "w") as f:
            # Write travel times
            f.write("Travel Times\n")

    def export_data(self):
        # Export collected data to a file (e.g., CSV)
        self.write_data()
        self.vehicle_data = []
        self.travel_times = []


if __name__ == "__main__":
    data_collector = DataCollector(folder="tmp/simple_model/", filename="simple_model")
    print(
        data_collector.create_filename(
            folder="tmp/simple_model/", filename="simple_model"
        )
    )
