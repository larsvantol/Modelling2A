# type: ignore
import json
import time
from typing import Callable

import numpy as np
from tqdm import tqdm

# pylint: disable=wrong-import-position
if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.getcwd())
# pylint: enable=wrong-import-position

from Analysis.DataCollector import DataCollector
from Behaviors.Behaviors import behavior_options
from GUI.set_simulation_settings_gui import get_simulation_settings
from Road.Lane import Lane
from Road.Road import Road
from Spawning.LaneDistributions import (
    LaneDistribution,
    lane_distribution_factory,
    lane_distributions,
)
from Spawning.Spawners import VehicleSpawner
from Vehicles.Vehicle import Vehicle


def simulate(simulation=None):
    """Simulate the traffic."""
    if simulation is None:
        print("Getting simulation settings")
        simulation = get_simulation_settings()
        print(json.dumps(simulation, indent=4))

    print("Storing simulation settings")

    datacollector = DataCollector(simulation["name"]["id"])

    def create_road() -> Road:
        road = Road(length=simulation["road"]["length"])

        for _ in range(simulation["road"]["lanes"]):
            road.add_lane(lane=Lane())

        return road

    road = create_road()

    def create_vehicle_factory() -> Callable[[], Vehicle]:
        behavior = behavior_options[simulation["vehicle"]["behavior"][0]]

        def vehicle_factory() -> Vehicle:
            desired_velocity = max(
                np.random.normal(
                    loc=simulation["vehicle"]["behavior_settings"][0],
                    scale=simulation["vehicle"]["behavior_settings"][1],
                ),
                0.01,
            )  # Velocity can't be 0 or negative

            behavior_parameters = {
                parameter: max(np.random.normal(value["mu"], value["sigma"]), 0.01)
                for parameter, value in simulation["vehicle"]["behavior"][1].items()
            }
            behavior_parameters["desired_velocity"] = desired_velocity

            return Vehicle(
                position=0,
                behavior_model=behavior(**behavior_parameters),
            )

        return vehicle_factory

    vehicle_factory = create_vehicle_factory()

    vehicle_spawner = VehicleSpawner(
        spawn_process=simulation["spawn"]["process"],
        lane_distribution_type=lane_distributions[simulation["lane_distribution"]],
        vehicle_factory=vehicle_factory,
        total_lanes=simulation["road"]["lanes"],
        road=road,
        data_collector=datacollector,
        cars_per_second=simulation["spawn"]["cars_per_second"],
        time_step=simulation["simulation"]["time_step"],
    )

    simulation_time = 0
    time_step = simulation["simulation"]["time_step"]
    steps = int(simulation["simulation"]["duration"] / simulation["simulation"]["time_step"])

    with datacollector as data_collector:
        start = time.perf_counter_ns()
        for simulation_step in tqdm(range(steps)):
            simulation_time = time_step * simulation_step
            data_collector.set_new_simulation_time(simulation_time)

            # Spawn new vehicles
            vehicle_spawner.spawn(simulation_time)

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

    return data_collector.return_path()


if __name__ == "__main__":
    simulate()
