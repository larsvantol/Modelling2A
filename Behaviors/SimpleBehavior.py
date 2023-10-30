"""Implementation of the simple behavior model and extensions of it."""
from __future__ import annotations

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


class SimpleBehavior(Behavior):
    """Implementation of the simple behavior model."""

    @staticmethod
    def standard_parameters() -> list[tuple[str, str, float, str]]:
        """Return the standard parameters for the Gipps behavior model."""

        return [
            ("Update Velocity Deviation", "update_velocity_deviation", (1 / 3.6), "m/s^2"),
        ]

    def __init__(
        self,
        desired_velocity: float,  # m/s
        initial_velocity_deviation: float = (4 / 3.6),  # m/s
        update_velocity_deviation: float = (1 / 3.6),  # m/s
    ) -> None:
        self.desired_velocity = desired_velocity  # m/s
        self.initial_velocity_deviation = initial_velocity_deviation  # m/s
        self.update_velocity_deviation = update_velocity_deviation  # m/s

    def set_initial_velocity(self, vehicle: Vehicle) -> None:
        # Take the desired velocity and add a random deviation
        vehicle.velocity = np.random.normal(self.desired_velocity, self.initial_velocity_deviation)

    def update(self, vehicle: Vehicle, road: Road, delta_t: float) -> None:
        # Take the current velocity and add a random deviation
        vehicle.velocity = max(
            0, np.random.normal(vehicle.velocity, self.update_velocity_deviation)
        )


class SimpleFollowingBehavior(SimpleBehavior):
    """Implementation of the simple behavior model."""

    @staticmethod
    def standard_parameters() -> list[tuple[str, str, float, str]]:
        """Return the standard parameters for the Gipps behavior model."""

        return [
            ("Update Velocity Deviation", "update_velocity_deviation", round(1 / 3.6, 2), "m/s^2"),
            ("Save Time", "save_time", 2, "s"),
        ]

    def __init__(
        self,
        desired_velocity: float,
        initial_velocity_deviation: float = (4 / 3.6),
        update_velocity_deviation: float = (1 / 3.6),
        save_time: float = 2,  # s
    ) -> None:
        super().__init__(desired_velocity, initial_velocity_deviation, update_velocity_deviation)
        self.save_time = save_time

    def update(self, vehicle: Vehicle, road: Road, delta_t: float) -> None:
        """Update the vehicle's state and position."""

        # First check if the vehicle can return to its original lane
        if return_if_possible(road, vehicle, delta_t):
            super().update(vehicle, road, delta_t)
            return

        # Now check if the vehicle is too close to the leading vehicle
        current_lane_index = road.get_current_lane_index(vehicle)
        lead_vehicle = road.lanes[current_lane_index].get_leading_vehicle(vehicle)
        if lead_vehicle:
            save_distance = calculate_save_distance_n_seconds_rule(vehicle, self.save_time)
            if lead_vehicle.position - vehicle.position < save_distance:
                # If the vehicle is too close, check if it can overtake
                if overtake_if_possible(road, vehicle, delta_t):
                    super().update(vehicle, road, delta_t)
                    return
                else:
                    # If the vehicle cannot overtake, reduce the velocity
                    vehicle.velocity = lead_vehicle.velocity
                    return

        super().update(vehicle, road, delta_t)

    def considers_lane_safe(self, vehicle: Vehicle, lane: Lane, delta_t: float) -> bool:
        """Check if the lane is safe to change to using the n seconds rule."""

        return is_outside_n_seconds_rule(vehicle, lane, self.save_time)


class SimpleFollowingExtendedBehavior(SimpleBehavior):
    """Implementation of an extension of the simple behavior model."""

    @staticmethod
    def standard_parameters() -> list[tuple[str, str, float, str]]:
        """Return the standard parameters for the Gipps behavior model."""

        return [
            ("Update Velocity Deviation", "update_velocity_deviation", round(1 / 3.6, 2), "m/s^2"),
            ("Save Time", "save_time", 2, "s"),
        ]

    def __init__(
        self,
        desired_velocity: float,
        initial_velocity_deviation: float = (4 / 3.6),
        update_velocity_deviation: float = (1 / 3.6),
        save_time: float = 2,  # s
    ) -> None:
        super().__init__(desired_velocity, initial_velocity_deviation, update_velocity_deviation)
        self.save_time = save_time

    def calculate_velocity(self, vehicle: Vehicle) -> float:
        """Calculate the velocity of the vehicle using a weighted average
        of the desired velocity and the calculated velocity."""

        velocity = max(
            0,
            0.99 * np.random.normal(vehicle.velocity, self.update_velocity_deviation)
            + 0.01 * self.desired_velocity,
        )

        return velocity

    def update(self, vehicle: Vehicle, road: Road, delta_t: float) -> None:
        """Update the vehicle's state and position."""

        # First check if the vehicle can return to its original lane
        # Use for this a 50% longer save time
        self.save_time *= 1.5
        if return_if_possible(road, vehicle, delta_t):
            vehicle.velocity = self.calculate_velocity(vehicle)
            self.save_time /= 1.5
            return
        self.save_time /= 1.5

        # Now check if the vehicle is too close to the leading vehicle
        current_lane_index = road.get_current_lane_index(vehicle)
        lead_vehicle = road.lanes[current_lane_index].get_leading_vehicle(vehicle)
        if lead_vehicle:
            save_distance = calculate_save_distance_n_seconds_rule(vehicle, self.save_time)
            if lead_vehicle.position - vehicle.position < save_distance:
                # If the vehicle is too close, check if it can overtake
                if overtake_if_possible(road, vehicle, delta_t):
                    vehicle.velocity = self.calculate_velocity(vehicle)
                    return
                else:
                    # If the vehicle cannot overtake, reduce the velocity with 10% per second
                    # So after 1 second 0.9, after 2 seconds 0.9**2, etc.
                    vehicle.velocity = min(vehicle.velocity * 0.9**delta_t, lead_vehicle.velocity)
                    return

        vehicle.velocity = self.calculate_velocity(vehicle)

    def considers_lane_safe(self, vehicle: Vehicle, lane: Lane, delta_t: float) -> bool:
        """Check if the lane is safe to change to using the n seconds rule."""

        return is_outside_n_seconds_rule(vehicle, lane, self.save_time)
