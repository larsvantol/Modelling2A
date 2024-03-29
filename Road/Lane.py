"""Implements the Lane class"""
from __future__ import annotations

import bisect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Vehicles.Vehicle import Vehicle


class Lane:
    """A lane on a road"""

    def __init__(self) -> None:
        self.vehicles: list[Vehicle] = []
        # 0 is the first vehicle in the lane, 1 is the second vehicle in the lane, etc.

    def add_vehicle_at_beginning(self, vehicle: Vehicle) -> None:
        """Add a vehicle to the lane at the beginning of the lane"""

        self.vehicles.append(vehicle)
        # Add a vehicle to the lane at the beginning

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Add a vehicle to the lane at the right position"""

        # Add a vehicle to the lane at the right position
        # -v.position because the list is sorted in descending order
        bisect.insort(self.vehicles, vehicle, key=lambda v: -v.position)

    def delete_vehicle(self, vehicle: Vehicle) -> None:
        """Delete a vehicle from the lane"""

        self.vehicles.remove(vehicle)

    def get_leading_vehicle(self, vehicle: Vehicle) -> Vehicle | None:
        """Get the vehicle in front of the given vehicle
        Returns None if there is no vehicle in front"""

        # index -1 is the leading one
        index = self.vehicles.index(vehicle)
        if index == 0:
            return None
        return self.vehicles[index - 1]

    def get_closest_vehicles(self, position: float) -> tuple[Vehicle | None, Vehicle | None]:
        """Get the vehicles in front of and behind the given position
        Returns a tuple of the vehicle in front and the vehicle behind a given position
        If there is no vehicle in front or behind, returns None
        (leading_vehicle, following_vehicle)"""

        # ToDo: What if the position is exactly the same as the position of a vehicle? # pylint: disable=fixme

        if len(self.vehicles) == 0:
            return (None, None)

        index = bisect.bisect_left(self.vehicles, -position, key=lambda v: -v.position)
        if index == len(self.vehicles):
            return (self.vehicles[index - 1], None)
        elif index == 0:
            return (None, self.vehicles[index])
        else:
            return (self.vehicles[index - 1], self.vehicles[index])

    def get_first_vehicle(self) -> Vehicle | None:
        """Get the first vehicle in the lane
        Returns None if there is no vehicle in the lane"""

        if len(self.vehicles) == 0:
            return None
        return self.vehicles[0]

    def get_last_vehicle(self) -> Vehicle | None:
        """Get the last vehicle in the lane
        Returns None if there is no vehicle in the lane"""

        if len(self.vehicles) == 0:
            return None
        return self.vehicles[-1]

    def sort(self):
        """Sort the vehicles in the lane based on position"""

        self.vehicles.sort(key=lambda v: -v.position)

    def __str__(self) -> str:
        return f"Lane: {self.vehicles}"
