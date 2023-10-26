from __future__ import annotations
from Behaviors.Behavior import Behavior
from Road.Road import Road


class Vehicle:
    def __init__(self, behavior_model: Behavior, position: float = 0) -> None:
        self.id = self.get_next_id()

        self.behavior_model = behavior_model
        self.width = 0.5
        self.length = 1.5

        self.position = position
        self.velocity = 0
        self.behavior_model.set_initial_velocity(self)

        self.previous_velocity = 0

    def update(self, road: Road, delta_t: float) -> None:
        self.previous_velocity = self.velocity
        self.position += self.velocity * delta_t
        self.behavior_model.update(
            vehicle=self,
            road=road,
            delta_t=delta_t,
        )

    @classmethod
    def get_next_id(cls):
        # Class method to get the next available ID
        if not hasattr(cls, "_id_counter"):
            cls._id_counter = 1
        else:
            cls._id_counter += 1
        return cls._id_counter
