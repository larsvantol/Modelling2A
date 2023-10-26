from __future__ import annotations
from typing import TYPE_CHECKING
from Road.Road import Road

if TYPE_CHECKING:
    from Vehicles.Vehicle import Vehicle
    from Road.Lane import Lane


class Behavior:
    def __init__(self) -> None:
        ...

    def update(self, vehicle: Vehicle, road: Road, delta_t: float):
        ...

    def set_initial_velocity(self, vehicle: Vehicle):
        ...

    def considers_lane_safe(self, lane: Lane) -> bool:
        ...
