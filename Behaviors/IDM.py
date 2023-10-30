"""Implements the Intelligent Driver Model (IDM) behavior."""

from __future__ import annotations

from math import sqrt

import numpy as np

from Behaviors.BehaviorBase import Behavior
from Behaviors.LaneChanging import (
    calculate_save_distance_n_seconds_rule,
    is_outside_n_seconds_rule,
    overtake_if_possible,
    return_if_possible,
)
from Road.Lane import Lane
from Road.Road import Road
from Vehicles.Vehicle import Vehicle


class IDMBehavior(Behavior):
    """Implementation of the IDM behavior model."""

    @staticmethod
    def standard_parameters() -> list[tuple[str, str, float, str]]:
        """Return the standard parameters for the IDM behavior model."""

        return [
            ("Time Headway", "time_headway", 1.5, "s"),
            ("Max Acceleration", "max_acceleration", 2, "m/s^2"),
            ("Comfortable Braking Deceleration", "comfortable_braking_deceleration", 3, "m/s^2"),
            ("Minimum Spacing", "minimum_spacing", 2, "m"),
            ("Acceleration Exponent", "acceleration_exponent", 4, ""),
        ]

    def __init__(
        self,
        desired_velocity: float,
        time_headway: float,
        max_acceleration: float,
        comfortable_braking_deceleration: float,
        minimum_spacing: float,
        acceleration_exponent: float,
    ) -> None:
        self.desired_velocity = desired_velocity
        self.time_headway = time_headway
        self.max_acceleration = max_acceleration
        self.comfortable_braking_deceleration = comfortable_braking_deceleration
        self.minimum_spacing = minimum_spacing
        self.acceleration_exponent = acceleration_exponent
        self.initial_velocity_deviation = 0.5

    def set_initial_velocity(self, vehicle: Vehicle) -> None:
        """Set the vehicle's initial velocity."""

        vehicle.velocity = np.random.normal(self.desired_velocity, self.initial_velocity_deviation)

    def update(self, vehicle: Vehicle, road: Road, delta_t: float) -> None:
        """Update the vehicle's state and position."""

        if return_if_possible(road, vehicle, delta_t):
            self.set_vehicle_velocity(vehicle, road, delta_t)
            return

        # Now check if the vehicle is too close to the leading vehicle
        current_lane_index = road.get_current_lane_index(vehicle)
        lead_vehicle = road.lanes[current_lane_index].get_leading_vehicle(vehicle)

        if lead_vehicle:
            save_distance = calculate_save_distance_n_seconds_rule(vehicle, self.time_headway)
            if lead_vehicle.position - vehicle.position < save_distance:
                # If the vehicle is too close, check if it can overtake
                if overtake_if_possible(road, vehicle, delta_t):
                    self.set_vehicle_velocity(vehicle, road, delta_t)
                    return

        self.set_vehicle_velocity(vehicle, road, delta_t)
        return

    def set_vehicle_velocity(self, vehicle: Vehicle, road: Road, delta_t: float) -> None:
        """Set the vehicle's velocity."""

        current_lane_index = road.get_current_lane_index(vehicle)
        lead_vehicle = road.lanes[current_lane_index].get_leading_vehicle(vehicle)
        vehicle.velocity = max(
            0,
            vehicle.velocity + self.calculate_acceleration(vehicle, lead_vehicle) * delta_t,
        )

    def calculate_acceleration(self, vehicle: Vehicle, lead_vehicle: Vehicle | None) -> float:
        """Calculate the vehicle's acceleration based on the IDM model."""

        if lead_vehicle is None:
            # No leading vehicle, accelerate to desired velocity
            return self.max_acceleration * (
                1 - (vehicle.velocity / self.desired_velocity) ** self.acceleration_exponent
            )

        # Calculate the net distance (spacing) to the leading vehicle
        net_distance = vehicle.position - lead_vehicle.position  # - lead_vehicle.length

        # Calculate the desired dynamic part of the minimum gap
        s_star = self.minimum_spacing + max(
            vehicle.velocity * self.time_headway
            + vehicle.velocity
            * (vehicle.velocity - lead_vehicle.velocity)
            / (2 * sqrt(self.max_acceleration * self.comfortable_braking_deceleration)),
            0,
        )

        # IDM acceleration equation
        return self.max_acceleration * (
            1
            - (vehicle.velocity / self.desired_velocity) ** self.acceleration_exponent
            - (s_star / net_distance) ** 2
        )

    def considers_lane_safe(self, vehicle: Vehicle, lane: Lane, delta_t: float) -> bool:
        """Check if the lane is safe to change to using the n seconds rule."""

        return is_outside_n_seconds_rule(vehicle, lane, self.time_headway)
