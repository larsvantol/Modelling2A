from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Vehicles.Vehicle import Vehicle


class Behavior:
    def __init__(self) -> None:
        ...

    def update(self, vehicle: Vehicle, lead_vehicle: Vehicle, delta_t: float):
        ...

    def set_initial_velocity(self, vehicle: Vehicle):
        ...
