"""This module contains functions for creating vehicle spawners."""
from __future__ import annotations

from typing import Callable

import numpy as np

from Analysis.DataCollector import DataCollector
from Road.Road import Road
from Spawning.LaneDistributions import lane_distribution_factory
from Vehicles.Vehicle import Vehicle


def poisson_new_cars(cars_per_second: float, delta_t: float) -> int:
    """Calculate the number of new cars using a Poisson process."""
    return np.random.default_rng().poisson(cars_per_second * delta_t)


def uniform_new_cars(cars_per_second: float, delta_t: float) -> int:
    """Calculate the number of new cars using a constant rate."""
    return round(cars_per_second * delta_t)


new_cars_factory: dict[str, Callable[[float, float], int]] = {
    "poisson": poisson_new_cars,
    "equal": uniform_new_cars,
}


class VehicleSpawner:
    """A vehicle spawner spawner."""

    def __init__(
        self,
        spawn_process: str,
        lane_distribution_type: str,
        vehicle_factory: Callable[[], Vehicle],
        total_lanes: int,
        road: Road,
        data_collector: DataCollector,
        cars_per_second: float,
        time_step: float,
    ) -> None:
        self.new_cars_process = new_cars_factory[spawn_process]
        self.lane_distribution = lane_distribution_factory(
            total_lanes=total_lanes, lane_distribution_type=lane_distribution_type
        )
        self.vehicle_factory = vehicle_factory
        self.road = road
        self.data_collector = data_collector
        self.cars_per_second = cars_per_second
        self.time_step = time_step

    def spawn(self, simulation_time: float) -> None:
        """Spawn vehicles on the road."""

        num_new_cars = self.new_cars_process(self.cars_per_second, self.time_step)

        cars_per_lane = self.lane_distribution(num_new_cars)

        for lane_index, num_new_cars_per_lane in enumerate(cars_per_lane):
            for _ in range(num_new_cars_per_lane):
                vehicle = self.vehicle_factory()

                self.road.add_vehicle(
                    vehicle=vehicle,
                    lane_index=lane_index,
                )
                self.data_collector.vehicle_added(vehicle, simulation_time)
