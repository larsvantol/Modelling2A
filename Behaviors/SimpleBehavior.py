from __future__ import annotations
from Behaviors.Behavior import Behavior
from Behaviors.LaneChanging import (
    overtake_if_possible,
    return_if_possible,
    is_outside_n_seconds_rule,
    calculate_save_distance_n_seconds_rule,
)
from Vehicles.Vehicle import Vehicle
from Road.Road import Road
from Road.Lane import Lane
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

    def update(self, vehicle: Vehicle, road: Road, delta_t: float):
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

    def update(self, vehicle: Vehicle, road: Road, delta_t: float):
        if return_if_possible(road, vehicle, delta_t):
            super().update(vehicle, road, delta_t)
            return

        # Now check if the vehicle is too close to the leading vehicle
        current_lane_index = road.get_current_lane_index(vehicle)
        lead_vehicle = road.lanes[current_lane_index].get_leading_vehicle(vehicle)
        if lead_vehicle:
            save_distance = calculate_save_distance_n_seconds_rule(
                vehicle, self.save_time
            )
            if lead_vehicle.position - vehicle.position < save_distance:
                # If the vehicle is too close, check if it can overtake
                if overtake_if_possible(road, vehicle, delta_t):
                    super().update(vehicle, lead_vehicle, delta_t)
                    return
                else:
                    # If the vehicle cannot overtake, reduce the velocity
                    vehicle.velocity = lead_vehicle.velocity
                    return

        super().update(vehicle, road, delta_t)

    def considers_lane_safe(self, vehicle: Vehicle, lane: Lane, delta_t: float) -> bool:
        # Check if the lane is safe to change to using the n seconds rule
        return is_outside_n_seconds_rule(vehicle, lane, self.save_time)


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

    def calculate_velocity(self, vehicle: Vehicle):
        velocity = (
            0.99 * np.random.normal(vehicle.velocity, self.update_velocity_deviation)
            + 0.01 * self.desired_velocity
        )
        if velocity < 0:
            velocity = 0

        return velocity

    def update(self, vehicle: Vehicle, road: Road, delta_t: float):
        if return_if_possible(road, vehicle, delta_t):
            vehicle.velocity = self.calculate_velocity(vehicle)
            return

        # Now check if the vehicle is too close to the leading vehicle
        current_lane_index = road.get_current_lane_index(vehicle)
        lead_vehicle = road.lanes[current_lane_index].get_leading_vehicle(vehicle)
        if lead_vehicle:
            save_distance = calculate_save_distance_n_seconds_rule(
                vehicle, self.save_time
            )
            if lead_vehicle.position - vehicle.position < save_distance:
                # If the vehicle is too close, check if it can overtake
                if overtake_if_possible(road, vehicle, delta_t):
                    vehicle.velocity = self.calculate_velocity(vehicle)
                    return
                else:
                    # If the vehicle cannot overtake, reduce the velocity
                    vehicle.velocity = lead_vehicle.velocity
                    return

        vehicle.velocity = self.calculate_velocity(vehicle)

    def considers_lane_safe(self, vehicle: Vehicle, lane: Lane, delta_t: float) -> bool:
        # Check if the lane is safe to change to using the n seconds rule
        return is_outside_n_seconds_rule(vehicle, lane, self.save_time)
