"""Factory for creating vehicles with a different behavior models."""
from __future__ import annotations

import numpy as np

from Behaviors.SimpleBehavior import SimpleFollowingExtendedBehavior
from Vehicles.Vehicle import Vehicle


def simple_vehicle_factory() -> Vehicle:
    """Create a vehicle with a simple behavior model."""
    # get desired_velocity from a normal distribution with mean 100 km/h and std 4 km/h
    desired_velocity = np.random.normal(100 / 3.6, 8 / 3.6)

    return Vehicle(
        position=0,
        behavior_model=SimpleFollowingExtendedBehavior(
            desired_velocity=desired_velocity,  # m/s
            save_time=2,  # s
        ),
    )
