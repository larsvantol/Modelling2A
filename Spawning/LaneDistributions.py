"""This module contains the lane distributions used 
to determine how many cars should be spawned in each lane."""
from __future__ import annotations

from typing import Callable


class LaneDistribution:
    """Base class for lane distributions.
    The lane distribution is used to determine how many cars should be spawned in each lane."""

    def __init__(self, total_lanes: int) -> None:
        self.total_lanes = total_lanes
        self.lane_probabilities: dict[int, float] = self.calculate_lane_probabilities()

    def calculate_lane_probabilities(self) -> dict[int, float]:
        """Calculate the probability of spawning a car in each lane.
        The sum of all probabilities should be 1."""
        raise NotImplementedError

    def __call__(self, total_new_cars: int) -> list[int]:
        """Calculate the number of cars that should be spawned in each lane."""
        cars_per_lane_unrounded = [
            self.lane_probabilities[i] * total_new_cars for i in range(self.total_lanes)
        ]
        cars_per_lane_rounded = [round(i) for i in cars_per_lane_unrounded]

        while sum(cars_per_lane_rounded) != total_new_cars:
            # optimize the number of cars per lane based on the rounding error
            differences_per_lane = [
                i - j for i, j in zip(cars_per_lane_unrounded, cars_per_lane_rounded)
            ]
            if sum(cars_per_lane_rounded) > total_new_cars:
                minimum_difference = min(differences_per_lane)
                # If there are multiple lanes with the same minimum difference,
                # choose the lane with the highest index
                index = (self.total_lanes - 1) - differences_per_lane[::-1].index(
                    minimum_difference
                )
                cars_per_lane_rounded[index] -= 1
            else:
                index = differences_per_lane.index(max(differences_per_lane))
                cars_per_lane_rounded[index] += 1

        return cars_per_lane_rounded


class TriangleLaneDistribution(LaneDistribution):
    """The probability of spawning a car in a lane is proportional to the lane index."""

    def calculate_lane_probabilities(self) -> dict[int, float]:
        p_i: Callable[[int], float] = lambda lane_index: (self.total_lanes - lane_index) / (
            (1 / 2) * self.total_lanes * (self.total_lanes + 1)
        )
        return {i: p_i(i) for i in range(self.total_lanes)}


class SumSquaredLaneDistribution(LaneDistribution):
    """The probability of spawning a car in a lane is proportional
    to the sum of the squares of the lane indices."""

    def __init__(self, total_lanes: int) -> None:
        super().__init__(total_lanes)
        self.squared_sum = sum([(i + 1) ** 2 for i in range(self.total_lanes)])

    def calculate_lane_probabilities(self) -> dict[int, float]:
        p_i: Callable[[int], float] = (
            lambda lane_index: (self.total_lanes - lane_index) / self.squared_sum
        )
        return {i: p_i(i) for i in range(self.total_lanes)}


class EqualLaneDistribution(LaneDistribution):
    """The probability of spawning a car in a lane is equal for all lanes."""

    def calculate_lane_probabilities(self) -> dict[int, float]:
        return {i: 1 / self.total_lanes for i in range(self.total_lanes)}


class AllInFirstLaneDistribution(LaneDistribution):
    """All cars are spawned in the first lane."""

    def calculate_lane_probabilities(self) -> dict[int, float]:
        p_i: Callable[[int], float] = lambda lane_index: 1 if lane_index == 0 else 0
        return {i: p_i(i) for i in range(self.total_lanes)}


class AllInLastLaneDistribution(LaneDistribution):
    """All cars are spawned in the last lane."""

    def calculate_lane_probabilities(self) -> dict[int, float]:
        p_i: Callable[[int], float] = (
            lambda lane_index: 1 if lane_index == self.total_lanes - 1 else 0
        )
        return {i: p_i(i) for i in range(self.total_lanes)}


def lane_distribution_factory(total_lanes: int, lane_distribution_type: str) -> LaneDistribution:
    """Factory function for creating lane distributions based on the lane distribution type."""

    if lane_distribution_type == "triangle" or lane_distribution_type == "linear":
        return TriangleLaneDistribution(total_lanes)
    elif lane_distribution_type == "sum_squared":
        return SumSquaredLaneDistribution(total_lanes)
    elif lane_distribution_type == "equal":
        return EqualLaneDistribution(total_lanes)
    elif lane_distribution_type == "all_in_first_lane":
        return AllInFirstLaneDistribution(total_lanes)
    elif lane_distribution_type == "all_in_last_lane":
        return AllInLastLaneDistribution(total_lanes)
    else:
        raise ValueError(f"Unknown lane distribution type: {lane_distribution_type}")


if __name__ == "__main__":
    lane_distribution = lane_distribution_factory(
        total_lanes=4,
        lane_distribution_type="linear",
    )
    print(lane_distribution.lane_probabilities)
    print(lane_distribution(10))
    print(lane_distribution(11))
