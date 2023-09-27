from __future__ import annotations
import numpy as np


class Vehicle:
    def __init__(self) -> None:
        ...

    def move(self, delta_t):
        ...


class Behavior:
    def __init__(self) -> None:
        ...

    def update(self, vehicle):
        ...

    def set_initial_velocity(self, vehicle):
        ...


class SimpleBehavior(Behavior):
    def __init__(
        self,
        desired_velocity: float,  # m/s
        initial_velocity_deviation: float = (4 / 3.6),  # m/s
        update_velocity_deviation: float = (1 / 3.6),  # m/s
    ) -> None:
        self.desired_velocity = desired_velocity  # m/s
        self.initial_velocity_deviation = initial_velocity_deviation  # m/s
        self.update_velocity_deviation = update_velocity_deviation  # m/s

    def set_initial_velocity(self, vehicle: Vehicle):
        # Take the desired velocity and add a random deviation
        vehicle.velocity = np.random.normal(
            self.desired_velocity, self.initial_velocity_deviation
        )

    def update(self, vehicle: Vehicle):
        # Take the current velocity and add a random deviation
        vehicle.velocity = np.random.normal(
            vehicle.velocity, self.update_velocity_deviation
        )
        if vehicle.velocity < 0:
            vehicle.velocity = 0


class Gipps(Behavior):
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

    def set_initial_velocity(self, vehicle: Vehicle):
        ...

    def update(self, vehicle: Vehicle, lead_vehicle: Vehicle, delta_t: float):
        # min [v + aΔt, v0, vsafe(s, vl )] gipps equation
        pass

    def calculate_safe_speed(
        self, leading_distance: float, leading_velocity: float, delta_t: float
    ) -> float:
        # −bT+ sqrt(b^2T^2+2b(s−s0)+vl^2)
        return self.maximum_acceleration * delta_t + (
            (self.maximum_acceleration**2) * (delta_t**2)
            + 2
            * self.maximum_acceleration
            * (leading_distance - self.comfortable_distance)
            + leading_velocity**2
        ) ** (0.5)


class Car(Vehicle):
    def __init__(self, behavior_model: Behavior, position: float = 0) -> None:
        self.behavior_model = behavior_model
        self.position = position
        self.behavior_model.set_initial_velocity(self)

    def update(self, delta_t):
        self.position += self.velocity * delta_t
        self.behavior_model.update(self)
