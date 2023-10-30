"""
This module contains the different behaviors that can be used by the vehicles.
"""
from typing import Type

from .BehaviorBase import Behavior
from .Gipps import GippsBehavior
from .IDM import IDMBehavior
from .SimpleBehavior import (
    SimpleBehavior,
    SimpleFollowingBehavior,
    SimpleFollowingExtendedBehavior,
)

behavior_options = {
    "Gipps Model": GippsBehavior,
    "Intelligent Driver Model": IDMBehavior,
    "Simple Model": SimpleBehavior,
    "Simple Following Model": SimpleFollowingBehavior,
    "Simple Following Extended Model": SimpleFollowingExtendedBehavior,
}

BehaviorType = Type[Behavior]
