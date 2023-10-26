from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Vehicles.Vehicle import Vehicle, Car

import bisect


class Lane:
    def __init__(self) -> None:
        self.vehicles: list[Vehicle] = []
        # 0 is the first vehicle in the lane, 1 is the second vehicle in the lane, etc.

    def add_vehicle_at_beginning(self, vehicle: Vehicle) -> None:
        self.vehicles.append(vehicle)
        # Add a vehicle to the lane at the beginning

    def add_vehicle(self, vehicle: Vehicle) -> None:
        # Add a vehicle to the lane at the right position
        # -v.position because the list is sorted in descending order
        bisect.insort(self.vehicles, vehicle, key=lambda v: -v.position)

    def delete_vehicle(self, vehicle: Vehicle) -> None:
        self.vehicles.remove(vehicle)

    def get_leading_vehicle(self, vehicle: Vehicle) -> Vehicle:
        # Get the vehicle in front of the given vehicle
        # index -1 is the leading one
        index = self.vehicles.index(vehicle)
        if index == 0:
            return None
        else:
            return self.vehicles[index - 1]

    def get_closest_vehicles(self, position: float) -> tuple[Vehicle, Vehicle]:
        # Returns a tuple of the vehicle in front and the vehicle behind a given position
        # If there is no vehicle in front or behind, returns None
        # (leading_vehicle, following_vehicle)

        # To Do: What if the position is exactly the same as the position of a vehicle?

        if len(self.vehicles) == 0:
            return (None, None)

        index = bisect.bisect_left(self.vehicles, -position, key=lambda v: -v.position)
        if index == len(self.vehicles):
            return (self.vehicles[index - 1], None)
        elif index == 0:
            return (None, self.vehicles[index])
        else:
            return (self.vehicles[index - 1], self.vehicles[index])

    def get_first_vehicle(self) -> Vehicle:
        if len(self.vehicles) == 0:
            return None
        else:
            return self.vehicles[0]

    def get_last_vehicle(self) -> Vehicle:
        if len(self.vehicles) == 0:
            return None
        else:
            return self.vehicles[-1]

    def sort(self):
        self.vehicles.sort(key=lambda v: -v.position)

    def __str__(self) -> str:
        return f"Lane: {self.vehicles}"
