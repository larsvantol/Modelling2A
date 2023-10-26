from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Vehicles.Vehicle import Vehicle

from Road.Lane import Lane

# from Vehicles.Vehicle import Vehicle


class Road:
    def __init__(self, length: float) -> None:
        self.lanes: dict[int, Lane] = {}
        self.vehicleslanes: dict[int, Vehicle] = {}
        self.length: float = length

    def num_lanes(self) -> int:
        return len(self.lanes)

    def add_lane(self, lane: Lane, index: int or None = None) -> None:
        if index is None:
            index = len(self.lanes)

        if index in self.lanes:
            raise ValueError(f"Lane {index} already exists")

        self.lanes[index] = lane

    def add_vehicle(self, vehicle: Vehicle, lane_index: int) -> None:
        if lane_index not in self.lanes:
            raise ValueError(f"Lane {lane_index} does not exist")

        lane = self.lanes[lane_index]
        lane.add_vehicle(vehicle)
        self.vehicleslanes[vehicle.id] = lane_index

    def delete_vehicle(self, vehicle: Vehicle) -> None:
        lane_index = self.vehicleslanes[vehicle.id]
        lane = self.lanes[lane_index]
        lane.delete_vehicle(vehicle)
        del self.vehicleslanes[vehicle.id]

    def get_current_lane_index(self, vehicle: Vehicle) -> int:
        return self.vehicleslanes[vehicle.id]

    def change_vehicle_lane(
        self,
        vehicle: Vehicle,
        new_lane_index: int,
        current_lane_index: int or None = None,
    ) -> None:
        # Check if the current lane is given else get the current lane
        if not (current_lane_index):
            # Check which lane the vehicle is currently in
            current_lane_index = self.get_current_lane_index(vehicle)

        # Check if the new lane exists
        if new_lane_index not in self.lanes:
            raise ValueError(f"Lane {new_lane_index} does not exist")

        # Check if the new lane and the current lane are one apart
        if abs(new_lane_index - current_lane_index) != 1:
            raise ValueError(
                f"Cannot change lane from {current_lane_index} to {new_lane_index}"
            )

        # Remove the vehicle from the current lane
        current_lane = self.lanes[current_lane_index]
        current_lane.delete_vehicle(vehicle)

        # Add the vehicle to the new lane
        new_lane = self.lanes[new_lane_index]
        new_lane.add_vehicle(vehicle)

        # Update the vehicle lane index
        self.vehicleslanes[vehicle.id] = new_lane_index
