from tqdm import tqdm
import numpy as np
import time
from decimal import Decimal
from collections.abc import Callable

# import the Vehicle class and the behavior models
from Vehicles.Vehicle import Vehicle
from Behaviors.SimpleBehavior import (
    SimpleBehavior,
    SimpleFollowingBehavior,
    SimpleFollowingExtendedBehavior,
)
from Behaviors.Gipps import GippsBehavior
from Analysis.DataCollector import DataCollector
from Road.Road import Road
from Road.Lane import Lane

simulation = {
    "name": {
        "id": "gipps_model_mul_lane",
        "description": "A simulation with the Gipps model",
    },
    "road": {
        "length": 500,
        "lanes": 2,
    },
    "simulation": {
        "time_step": 0.1,
        "duration": 10 * 60 * 60,
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
            behavior_model=GippsBehavior(
                maximum_acceleration=1.5,  # m/s^2
                maximum_deceleration=1.0,  # m/s^2
                desired_velocity=desired_velocity,  # m/s
                apparent_reaction_time=1.1,  # s
            ),
        )

    CARS_PER_SECOND = 0.4
    simulation["spawning"] = {
        "type": "poisson",
        "cars_per_second": CARS_PER_SECOND,
    }

    def spawn_vehicles(
        road: Road, data_collector: DataCollector, simulation_time: float
    ) -> None:
        # Spawn new cars using a Poisson process

        for _ in range(
            np.random.default_rng().poisson(
                CARS_PER_SECOND * simulation["simulation"]["time_step"]
            )
        ):
            vehicle = create_vehicle()
            road.add_vehicle(
                vehicle=vehicle,
                lane_index=0,
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

    # Run the simulation
    with DataCollector(simulation["name"]["id"]) as data_collector:
        for simulation_step in tqdm(range(steps)):
            simulation_time = time_step * simulation_step
            data_collector.add_new_simulation_time(simulation_time)

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
                while (len(lane.vehicles)) > 0 and (
                    lane.vehicles[0].position > road.length
                ):
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
    simulate()
