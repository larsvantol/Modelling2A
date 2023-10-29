import os
import time
from collections.abc import Callable
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
from Road.Lane import Lane
from Road.Road import Road

# import the Vehicle class and the behavior models
from Vehicles.Vehicle import Vehicle

simulation = {
    "name": {
        "id": "simple_following_extended_model_mul_lane",
        "description": "A simulation with the Simple Following Extended model",
    },
    "road": {
        "length": 500,
        "lanes": 5,
    },
    "simulation": {
        "time_step": 0.1,
        "duration": 1 * 60 * 60,
    },
}


def create_road() -> Road:
    road = Road(length=simulation["road"]["length"])

    for _ in range(simulation["road"]["lanes"]):
        road.add_lane(lane=Lane())

    return road


def create_vehicle_spawner() -> Callable[[Road, DataCollector, float], None]:
    def create_vehicle() -> Vehicle:
        # get desired_velocity from a normal distribution with mean 100 km/h and std 4 km/h
        desired_velocity = np.random.normal(100 / 3.6, 8 / 3.6)

        return Vehicle(
            position=0,
            behavior_model=SimpleFollowingExtendedBehavior(
                desired_velocity=desired_velocity,  # m/s
                save_time=2,  # s
            ),
        )

    CARS_PER_SECOND = 0.2 * 5
    simulation["spawning"] = {
        "type": "poisson",
        "cars_per_second": CARS_PER_SECOND,
    }

    def spawn_vehicles(road: Road, data_collector: DataCollector, simulation_time: float) -> None:
        # Spawn new cars using a Poisson process

        num_new_cars = np.random.default_rng().poisson(
            CARS_PER_SECOND * simulation["simulation"]["time_step"]
        )

        # # p_i = (lane_index + 1) / sum from 1 till num of lanes (i**2 for i in range(1, lanes + 1))
        # # # probability of spawning in lane i
        # p_i = lambda lane_index, total_lanes: (lane_index + 1) / sum(
        #     [(i + 1) ** 2 for i in range(total_lanes)]
        # )

        # p_i = (lane_index + 1) / triangle_number(total_lanes)
        # # probability of spawning in lane i
        p_i = lambda lane_index, total_lanes: (lane_index + 1) / (
            (1 / 2) * total_lanes * (total_lanes + 1)
        )

        cars_per_lane_unrounded = [
            int(p_i(i, simulation["road"]["lanes"]) * num_new_cars)
            for i in range(simulation["road"]["lanes"])
        ]
        cars_per_lane_rounded = [round(i) for i in cars_per_lane_unrounded]

        while sum(cars_per_lane_rounded) != num_new_cars:
            # optimize the number of cars per lane based on the rounding error
            differences_per_lane = [
                abs(i - j) for i, j in zip(cars_per_lane_unrounded, cars_per_lane_rounded)
            ]
            index = differences_per_lane.index(max(differences_per_lane))
            if cars_per_lane_rounded[index] > cars_per_lane_rounded[index]:
                cars_per_lane_rounded[index] -= 1
            else:
                cars_per_lane_rounded[index] += 1

        for lane_index, num_new_cars in enumerate(cars_per_lane_rounded):
            for _ in range(num_new_cars):
                vehicle = create_vehicle()

                road.add_vehicle(
                    vehicle=vehicle,
                    lane_index=lane_index,
                )
                data_collector.vehicle_added(vehicle, simulation_time)

    return spawn_vehicles


def simulate():
    # Simulation setup
    time_step = simulation["simulation"]["time_step"]  # s
    simulation_duration = simulation["simulation"]["duration"]  # s

    road = create_road()
    vehicle_spawner = create_vehicle_spawner()

    # Simulation start
    simulation_time = 0
    start = time.perf_counter_ns()

    steps = int(simulation_duration / time_step)

    print(f"Running simulation for {steps} steps")

    # Run the simulation
    with DataCollector(simulation["name"]["id"]) as data_collector:
        for simulation_step in tqdm(range(steps)):
            simulation_time = time_step * simulation_step
            data_collector.set_new_simulation_time(simulation_time)

            # Spawn new vehicles
            vehicle_spawner(road, data_collector, simulation_time)

            # Update all vehicles
            for lane_index, lane in road.lanes.items():
                for vehicle in lane.vehicles:
                    # Update the vehicle
                    vehicle.update(road=road, delta_t=time_step)

                    # Collect data for the vehicle
                    data_collector.collect_data(vehicle=vehicle, lane_index=lane_index)

            for lane_index, lane in road.lanes.items():
                # Remove vehicles that have left the road
                while (len(lane.vehicles)) > 0 and (lane.vehicles[0].position > road.length):
                    data_collector.vehicle_deleted(lane.vehicles[0], simulation_time)
                    road.delete_vehicle(lane.vehicles[0])

        # Simulation end
        end = time.perf_counter_ns()

    simulation["process"] = {
        "steps": steps,
        "runtime": (end - start) / 1e9,
    }
    print(f"Simulation took {simulation['process']['runtime']:.2f} seconds")

    # Add extra data to the data file
    data_collector.add_extra_data(simulation)


if __name__ == "__main__":
    # Change working directory to a level above the directory of this file
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    simulate()
