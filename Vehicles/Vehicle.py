from __future__ import annotations
from Behaviors.Behavior import Behavior


class Vehicle:
    def __init__(self) -> None:
        self.id = self.get_next_id()

    def move(self, delta_t):
        ...

    @classmethod
    def get_next_id(cls):
        # Class method to get the next available ID
        if not hasattr(cls, "_id_counter"):
            cls._id_counter = 1
        else:
            cls._id_counter += 1
        return cls._id_counter


class Car(Vehicle):
    def __init__(self, behavior_model: Behavior, position: float = 0) -> None:
        super().__init__()
        self.behavior_model = behavior_model
        self.position = position
        self.behavior_model.set_initial_velocity(self)

    def update(self, leading_vehicle: Vehicle, delta_t: float) -> None:
        self.position += self.velocity * delta_t
        self.behavior_model.update(self, leading_vehicle, delta_t)
