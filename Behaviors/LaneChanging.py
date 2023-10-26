from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Vehicles.Vehicle import Vehicle

from Road.Road import Road
from Road.Lane import Lane


def overtake_if_possible(road: Road, vehicle: Vehicle, delta_t: float) -> None:
    current_lane_index = road.get_current_lane_index(vehicle=vehicle)

    # If there is no next lane, we cannot overtake
    if current_lane_index + 1 >= road.num_lanes():
        return

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


def return_if_possible(road: Road, vehicle: Vehicle, delta_t: float) -> None:
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


def is_outside_n_seconds_rule(vehicle: Vehicle, lane: Lane, safe_seconds: float):
    # First calculate the safe distance
    safe_distance = calculate_save_distance_n_seconds_rule(vehicle, safe_seconds)

    # Get vehicles in front and behind the vehicle
    leading_vehicle, following_vehicle = lane.get_closest_vehicles(vehicle.position)

    # Check if the vehicle is too close to the leading vehicle
    if leading_vehicle:
        if (
            leading_vehicle.position - leading_vehicle.length
        ) - vehicle.position < safe_distance:
            return False

    # Check if the vehicle is too close to the following vehicle
    if following_vehicle:
        if (
            vehicle.position - vehicle.length
        ) - following_vehicle.position < safe_distance:
            return False

    return True


def calculate_save_distance_n_seconds_rule(vehicle: Vehicle, safe_seconds: float):
    return vehicle.velocity * safe_seconds
