import os
import re
import time


class DataCollector:
    def __init__(self, folder, filename):
        self.vehicle_data = []  # Not needed anymore?
        self.travel_times = []  # Not needed anymore?
        self.path = self.create_filename(folder, filename)

        self.iteration = 0
        self.maximum_data = 1000

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
        # Collect data for each vehicle (e.g., position, velocity, lane)
        self.iteration += 1
        self.vehicle_data.append(
            {
                "position": vehicle.position,
                "velocity": vehicle.velocity,
            }
        )
        if self.iteration >= self.maximum_data:
            print(f"Maximum reached: {self.iteration} / {self.maximum_data}")
            start = time.perf_counter_ns()
            self.export_data()
            self.iteration = 0
            print((time.perf_counter_ns() - start) / 1e9)

    def record_travel_time(self, vehicle, simulation_time):
        # Calculate and record the travel time of a vehicle
        if vehicle.velocity > 0:
            travel_time = simulation_time  # Assuming simulation_time is in seconds
            self.travel_times.append(travel_time)

    def export_data(self):
        # Export collected data to a file (e.g., CSV)

        with open(f"{self.path}_vehicle_data.csv", "w") as f:
            # Write header row
            f.write("vehicle_id,position,velocity,lane\n")
            # Write data rows
            for vehicle_data in self.vehicle_data:
                f.write(f"{vehicle_data['position']},{vehicle_data['velocity']}\n")

        with open(f"{self.path}_travel_times.csv", "w") as f:
            # Write travel times
            f.write("Travel Times\n")
            for travel_time in self.travel_times:
                f.write(f"{travel_time}\n")


if __name__ == "__main__":
    data_collector = DataCollector(folder="tmp/simple_model/", filename="simple_model")
    print(
        data_collector.create_filename(
            folder="tmp/simple_model/", filename="simple_model"
        )
    )
