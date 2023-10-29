import time
from decimal import Decimal

import numpy as np
from tqdm import tqdm

from Analysis.DataCollector import DataCollector
from Behaviors.Gipps import GippsBehavior
from Behaviors.SimpleBehavior import (
    SimpleBehavior,
    SimpleFollowingBehavior,
    SimpleFollowingExtendedBehavior,
)

# import the Vehicle class and the behavior models
from Vehicles.Vehicle import Car


def create_car():
    # get desired_velocity from a normal distribution with mean 100 km/h and std 4 km/h
    # desired_velocity = np.random.normal(100 / 3.6, 4 / 3.6)
    # return Car(
    #     position=0,
    #     behavior_model=GippsBehavior(
    #         maximum_acceleration=1.5,  # m/s^2
    #         maximum_deceleration=1.0,  # m/s^2
    #         desired_velocity=desired_velocity,  # m/s
    #         apparent_reaction_time=1.1,  # s
    #     ),
    # )
    # return Car(
    #     position=0,
    #     behavior_model=SimpleFollowingBehavior(desired_velocity=(100 / 3.6)),
    # )
    return Car(
        position=0,
        behavior_model=SimpleFollowingExtendedBehavior(desired_velocity=(100 / 3.6)),
    )


def spawn_car(road, data_collector, simulation_time):
    car = create_car()
    road.append(car)
    data_collector.car_added(car, simulation_time)


if __name__ == "__main__":
    # Simulation setup
    time_step = 0.1  # s
    simulation_duration = 10 * 60 * 60  # s
    road_length = 5000  # m

    data_collector = DataCollector(
        # folder="tmp/simplefollowing_model/",
        # filename="simplefollowing_model"
        # folder="tmp/gipps_model/",
        # filename="gipps_model",
        folder="tmp/simplefollowing_extended_model/",
        filename="simplefollowing_extended_model",
    )

    road = []

    # Simulation loop
    start = time.perf_counter_ns()

    simulation_time = 0

    # Spawn first car
    spawn_car(road, data_collector, simulation_time)

    for simulation_step in tqdm(range(int(simulation_duration / time_step))):
        data_collector.set_new_simulation_time(simulation_time)

        # Spawn new cars using a Poisson process
        cars_per_second = 0.1
        for i in range(np.random.default_rng().poisson(cars_per_second * time_step)):
            spawn_car(road, data_collector, simulation_time)

        # Update all cars
        for i, vehicle in enumerate(road):
            leading_vehicle = road[i - 1] if i > 0 else None
            vehicle.update(leading_vehicle=leading_vehicle, delta_t=time_step)

        # Collect data for vehicles
        for vehicle in road:
            data_collector.collect_data(vehicle=vehicle)

        # Check if road is empty
        if len(road) != 0:
            # Check if the leading vehicle has completed its journey and record travel time
            first_vehicle = road[0]
            if first_vehicle.position >= road_length:
                # print("first:", first_vehicle.position)
                # Record the total travel time
                data_collector.vehicle_deleted(first_vehicle, simulation_time)
                # Remove the vehicle from the road
                road.remove(first_vehicle)

        simulation_time += time_step
        simulation_time = round(simulation_time, 1)

    stop = time.perf_counter_ns()
    print(f"Duration: {(stop - start) / 1e9} s")

    # Export collected data
    data_collector.export_data()
