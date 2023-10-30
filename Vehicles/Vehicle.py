"""Implementation of the Vehicle class."""
from __future__ import annotations

from Behaviors.BehaviorBase import Behavior
from Road.Road import Road


class Vehicle:
    """A vehicle class that contains a behavior model and a position on the road."""

    def __init__(self, behavior_model: Behavior, position: float = 0) -> None:
        self.id = self.get_next_id()

        self.behavior_model: Behavior = behavior_model
        self.width: float = 0.5
        self.length: float = 1.5

        self.position: float = position
        self.velocity: float = 0
        self.behavior_model.set_initial_velocity(self)

        self.previous_velocity: float = 0

    def update(self, road: Road, delta_t: float) -> None:
        """Update the vehicle's state and position."""

        self.previous_velocity = self.velocity
        self.position += self.velocity * delta_t
        self.behavior_model.update(
            vehicle=self,
            road=road,
            delta_t=delta_t,
        )

    @classmethod
    def get_next_id(cls):
        """Return the next available ID."""

        if not hasattr(cls, "_id_counter"):
            cls._id_counter = 1
        else:
            cls._id_counter += 1
        return cls._id_counter
