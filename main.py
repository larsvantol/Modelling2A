from tqdm import tqdm
import time

# import the Vehicle class and the behavior models
from Vehicle import Car, SimpleBehavior
from DataCollector import DataCollector

if __name__ == "__main__":
    # Simulation setup
    time_step = 0.1  # s
    # simulation_duration = 1 * 60 * 60  # s
    road_length = 5000  # m

    data_collector = DataCollector(folder="tmp/simple_model/", filename="simple_model")

    for _ in tqdm(range(1000)):
        simulation_time = 0
        # Create vehicle
        vehicle1 = Car(
            position=0,
            behavior_model=SimpleBehavior(desired_velocity=(100 / 3.6)),
        )

        while vehicle1.position < road_length:
            # data_collector.collect_data(vehicle1)
            simulation_time += time_step
            vehicle1.update(time_step)

        data_collector.record_travel_time(vehicle1, simulation_time)

    # # Simulation loop
    # for simulation_time in range(int(simulation_duration / time_step)):
    #     vehicle1.update(time_step)
    #     # Collect data for vehicles
    #     data_collector.collect_data(vehicle1)

    #     # Check if a vehicle has completed its journey and record travel time
    #     if vehicle1.position >= road_length:
    #         data_collector.record_travel_time(vehicle1, simulation_time)
    #         # exit simulation
    #         break

    # Export collected data
    data_collector.export_data()

    # Analyze travel time distribution
    # Calculate statistics such as mean, median, and create histograms, etc., using the travel times data
    # You can use libraries like NumPy and Matplotlib for data analysis and visualization
