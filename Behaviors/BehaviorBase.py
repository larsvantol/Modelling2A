"""This module contains the Behavior class, which is the base class for all behaviors."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from Road.Road import Road

if TYPE_CHECKING:
    from Road.Lane import Lane
    from Vehicles.Vehicle import Vehicle


class Behavior(ABC):
    """Base class for behaviors."""

    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def update(self, vehicle: Vehicle, road: Road, delta_t: float):
        """Update the vehicle's state and position."""

    @abstractmethod
    def set_initial_velocity(self, vehicle: Vehicle):
        """Set the vehicle's initial velocity."""

    @abstractmethod
    def considers_lane_safe(self, vehicle: Vehicle, lane: Lane, delta_t: float) -> bool:
        """Return whether the lane is safe to change to."""

    @staticmethod
    @abstractmethod
    def standard_parameters() -> list[tuple[str, str, float, str]]:
        """Return the standard parameters for the behavior model."""
