"""This file contains functions that are used to change lanes."""
from __future__ import annotations

from typing import TYPE_CHECKING

from Road.Lane import Lane
from Road.Road import Road

if TYPE_CHECKING:
    from Vehicles.Vehicle import Vehicle


def overtake_if_possible(road: Road, vehicle: Vehicle, delta_t: float) -> bool:
    """Go to a higher lane if it is safe to do so, and return whether the vehicle changed lanes."""
    current_lane_index = road.get_current_lane_index(vehicle=vehicle)

    # If there is no next lane, we cannot overtake
    if current_lane_index + 1 >= road.num_lanes():
        return False

    next_lane = road.lanes[current_lane_index + 1]

    # If the next lane is safe, we can overtake
    if vehicle.behavior_model.considers_lane_safe(
        vehicle=vehicle,
        lane=next_lane,
        delta_t=delta_t,
    ):
        road.change_vehicle_lane(
            vehicle=vehicle,
            new_lane_index=current_lane_index + 1,
            current_lane_index=current_lane_index,
        )
        return True
    return False


def return_if_possible(road: Road, vehicle: Vehicle, delta_t: float) -> bool:
    """Go to a lower lane if it is safe to do so."""
    current_lane_index = road.get_current_lane_index(vehicle)

    # If the vehicle is in the first lane, it cannot return
    if current_lane_index == 0:
        return False

    previous_lane = road.lanes[current_lane_index - 1]

    if vehicle.behavior_model.considers_lane_safe(
        vehicle=vehicle,
        lane=previous_lane,
        delta_t=delta_t,
    ):
        road.change_vehicle_lane(
            vehicle=vehicle,
            new_lane_index=current_lane_index - 1,
            current_lane_index=current_lane_index,
        )
        return True
    return False


def is_outside_n_seconds_rule(vehicle: Vehicle, lane: Lane, safe_seconds: float) -> bool:
    """Return whether the vehicle is outside of the n seconds rule."""
    # First calculate the safe distance
    safe_distance = calculate_save_distance_n_seconds_rule(vehicle, safe_seconds)

    # Get vehicles in front and behind the vehicle
    leading_vehicle, following_vehicle = lane.get_closest_vehicles(vehicle.position)

    # Check if the vehicle is too close to the leading vehicle
    if leading_vehicle:
        if (leading_vehicle.position - leading_vehicle.length) - vehicle.position < safe_distance:
            return False

    # Check if the vehicle is too close to the following vehicle
    if following_vehicle:
        if (vehicle.position - vehicle.length) - following_vehicle.position < safe_distance:
            return False

    return True


def calculate_save_distance_n_seconds_rule(vehicle: Vehicle, safe_seconds: float) -> float:
    """Calculate the safe distance using the n seconds rule."""
    return vehicle.velocity * safe_seconds
