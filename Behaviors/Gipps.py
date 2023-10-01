from __future__ import annotations
from Behaviors.Behavior import Behavior
from Vehicles.Vehicle import Vehicle
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

    def set_initial_velocity(self, vehicle: Vehicle):
        vehicle.velocity = np.random.normal(
            self.desired_velocity, self.initial_velocity_deviation
        )

    def update(self, vehicle: Vehicle, lead_vehicle: Vehicle, delta_t: float):
        vehicle.velocity = self.calculate_new_velocity(
            vehicle=vehicle, lead_vehicle=lead_vehicle, delta_t=delta_t
        )

    def calculate_new_velocity(
        self, vehicle: Vehicle, lead_vehicle: Vehicle, delta_t: float
    ):
        # min [v + aΔt, v0, vsafe(s, vl )] gipps equation
        leading_distance = (
            lead_vehicle.position - vehicle.position if lead_vehicle else float("inf")
        )
        leading_velocity = lead_vehicle.velocity if lead_vehicle else 0
        return min(
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
