from __future__ import annotations
from Behaviors.Behavior import Behavior
from Behaviors.LaneChanging import (
    overtake_if_possible,
    return_if_possible,
    is_outside_n_seconds_rule,
    calculate_save_distance_n_seconds_rule,
)
from Vehicles.Vehicle import Vehicle
from Road.Lane import Lane
from Road.Road import Road
import numpy as np


class GippsBehavior(Behavior):
    def __init__(
        self,
        maximum_acceleration: float,
        maximum_deceleration: float,
        desired_velocity: float,
        apparent_reaction_time: float,
    ) -> None:
        self.maximum_acceleration = maximum_acceleration
        self.maximum_deceleration = maximum_deceleration
        self.desired_velocity = desired_velocity
        self.apparent_reaction_time = apparent_reaction_time
        self.comfortable_distance = 2  # m
        self.initial_velocity_deviation = 0.5  # m/s

        self.velocities = (0, 0, 0)  # Acceleration, Desired Velocity, Safe Velocity

    def set_initial_velocity(self, vehicle: Vehicle):
        vehicle.velocity = np.random.normal(
            self.desired_velocity, self.initial_velocity_deviation
        )

    def set_vehicle_velocity(self, vehicle: Vehicle, road: Road, delta_t: float):
        current_lane_index = road.get_current_lane_index(vehicle)
        lead_vehicle = road.lanes[current_lane_index].get_leading_vehicle(vehicle)
        self.velocities = self.calculate_new_velocities(vehicle, lead_vehicle, delta_t)
        vehicle.velocity = min(self.velocities)

    def update(self, vehicle: Vehicle, road: Road, delta_t: float):
        if return_if_possible(road, vehicle, delta_t):
            self.set_vehicle_velocity(vehicle, road, delta_t)
            return

        # Now check if the vehicle is too close to the leading vehicle
        current_lane_index = road.get_current_lane_index(vehicle)
        lead_vehicle = road.lanes[current_lane_index].get_leading_vehicle(vehicle)

        if lead_vehicle:
            save_distance = calculate_save_distance_n_seconds_rule(
                vehicle, self.apparent_reaction_time
            )
            if lead_vehicle.position - vehicle.position < save_distance:
                # If the vehicle is too close, check if it can overtake
                if overtake_if_possible(road, vehicle, delta_t):
                    self.set_vehicle_velocity(vehicle, road, delta_t)
                    return

        self.set_vehicle_velocity(vehicle, road, delta_t)
        return

    def calculate_new_velocities(
        self, vehicle: Vehicle, lead_vehicle: Vehicle, delta_t: float
    ):
        # min [v + aΔt, v0, vsafe(s, vl )] gipps equation
        leading_distance = (
            (lead_vehicle.position - lead_vehicle.length) - vehicle.position
            if lead_vehicle
            else float("inf")
        )
        leading_velocity = lead_vehicle.velocity if lead_vehicle else 0

        return (
            vehicle.velocity + self.maximum_acceleration * delta_t,
            self.desired_velocity,
            self.calculate_safe_speed(
                leading_distance=leading_distance,
                leading_velocity=leading_velocity,
                delta_t=delta_t,
            ),
        )

    def calculate_safe_speed(
        self, leading_distance: float, leading_velocity: float, delta_t: float
    ) -> float:
        # safe_speed = −bT+ sqrt(b^2T^2+2b(s−s0)+vl^2)
        return self.maximum_acceleration * delta_t + (
            (self.maximum_acceleration**2) * (delta_t**2)
            + 2
            * self.maximum_acceleration
            * (leading_distance - self.comfortable_distance)
            + leading_velocity**2
        ) ** (0.5)

    def considers_lane_safe(self, vehicle: Vehicle, lane: Lane, delta_t: float) -> bool:
        # Check if the lane is safe to change to using the n seconds rule
        return is_outside_n_seconds_rule(vehicle, lane, self.apparent_reaction_time)
