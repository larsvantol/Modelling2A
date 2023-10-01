from __future__ import annotations
from Behaviors.Behavior import Behavior
from Vehicles.Vehicle import Vehicle
import numpy as np


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

    def update(self, vehicle: Vehicle, lead_vehicle: Vehicle, delta_t: float):
        # Take the current velocity and add a random deviation
        vehicle.velocity = np.random.normal(
            vehicle.velocity, self.update_velocity_deviation
        )
        if vehicle.velocity < 0:
            vehicle.velocity = 0


class SimpleFollowingBehavior(SimpleBehavior):
    def __init__(
        self,
        desired_velocity: float,
        initial_velocity_deviation: float = (4 / 3.6),
        update_velocity_deviation: float = (1 / 3.6),
        save_time: float = 2,  # s
    ) -> None:
        super().__init__(
            desired_velocity, initial_velocity_deviation, update_velocity_deviation
        )
        self.save_time = save_time

    def set_initial_velocity(self, vehicle: Vehicle):
        return super().set_initial_velocity(vehicle)

    def calculate_save_distance(self, vehicle: Vehicle):
        return vehicle.velocity * self.save_time

    def update(self, vehicle: Vehicle, lead_vehicle: Vehicle, delta_t: float):
        super().update(vehicle, lead_vehicle, delta_t)

        # Now check if the vehicle is too close to the leading vehicle
        if lead_vehicle:
            save_distance = self.calculate_save_distance(vehicle)
            if lead_vehicle.position - vehicle.position < save_distance:
                # If the vehicle is too close, reduce the velocity
                vehicle.velocity = lead_vehicle.velocity


class SimpleFollowingExtendedBehavior(SimpleBehavior):
    def __init__(
        self,
        desired_velocity: float,
        initial_velocity_deviation: float = (4 / 3.6),
        update_velocity_deviation: float = (1 / 3.6),
        save_time: float = 2,  # s
    ) -> None:
        super().__init__(
            desired_velocity, initial_velocity_deviation, update_velocity_deviation
        )
        self.save_time = save_time

    def set_initial_velocity(self, vehicle: Vehicle):
        return super().set_initial_velocity(vehicle)

    def calculate_save_distance(self, vehicle: Vehicle):
        return vehicle.velocity * self.save_time

    def update(self, vehicle: Vehicle, lead_vehicle: Vehicle, delta_t: float):
        vehicle.velocity = (
            0.99 * np.random.normal(vehicle.velocity, self.update_velocity_deviation)
            + 0.01 * self.desired_velocity
        )
        if vehicle.velocity < 0:
            vehicle.velocity = 0

        # Now check if the vehicle is too close to the leading vehicle
        if lead_vehicle:
            save_distance = self.calculate_save_distance(vehicle)
            if lead_vehicle.position - vehicle.position < save_distance:
                # If the vehicle is too close, reduce the velocity
                vehicle.velocity = lead_vehicle.velocity
