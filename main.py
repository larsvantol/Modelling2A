from typing import Self
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
from colors import random_color


class Road:
    def __init__(self, length, num_of_lanes) -> None:
        # length: length of the road in meters
        # num_of_lanes: number of lanes on the road
        self.length = length
        self.num_of_lanes = num_of_lanes
        self.lanes = {i: [] for i in range(num_of_lanes)}
        self.lane_width = 5  # m

    def add_car(self, car, lane_index) -> None:
        # Adds a car to the road on the lane given the lane_index
        self.lanes[lane_index].append(car)
        print(f"Car {car.name} has entered the road on lane {lane_index}")

    def remove_car(self, car, lane_index) -> None:
        # Removes a car from the road on the lane given the lane_index
        if car in self.lanes[lane_index]:
            self.lanes[lane_index].remove(car)
            print(f"Car {car.name} has left the road")

    def move_vehicle_to_lane(self, vehicle, from_lane, to_lane):
        if from_lane != to_lane:
            self.lanes[from_lane].remove(vehicle)
            self.lanes[to_lane].append(vehicle)
            vehicle.lane = to_lane

    def cars_on_road(self) -> bool:
        # Returns True if there are cars on the road
        return any(self.lanes.values())

    def str_of_cars_on_road(self) -> str:
        # A string representation of the cars on the road
        str_cars_on_road = ""
        for lane_index in range(self.num_of_lanes):
            str_cars_on_road += f"Lane {lane_index}:"
            for car in self.lanes[lane_index]:
                str_cars_on_road += f"\n\t{car},"
            str_cars_on_road += "\n"
        return str_cars_on_road

    def move_cars(self, delta_t) -> None:
        # Moves all cars on the road
        for lane_index in range(self.num_of_lanes):
            for car in self.lanes[lane_index]:
                car.move(delta_t=delta_t, road=self, lane_index=lane_index)
                if car.x > self.length and car in self.lanes[lane_index]:
                    self.remove_car(car, lane_index=lane_index)

    def __str__(self) -> str:
        # A string representation of the details of the road and the cars on it
        road_details = (
            f"Road:\n\tlength = \t{self.length} m\n\tlanes = \t{self.num_of_lanes}"
        )
        car_details = self.str_of_cars_on_road()
        return f"{road_details}\n{car_details}"

    def show_graphical_representation(self):
        # Show a graphical representation of the road and the cars on it

        # First loop over all cars and plot them on the middle of the lane
        for lane_index in range(self.num_of_lanes):
            for car in self.lanes[lane_index]:
                square = car.graphical_representation(
                    y=(lane_index + 0.5) * self.lane_width
                )
                plt.gca().add_patch(square)

        # Next loop over all lanes and plot them
        for lane_index in range(self.num_of_lanes):
            plt.plot(
                [0, self.length],
                [lane_index * self.lane_width, lane_index * self.lane_width],
                "k",
            )
        plt.plot(
            [0, self.length],
            [(lane_index + 1) * self.lane_width, (lane_index + 1) * self.lane_width],
            "k",
        )


class Car:
    def __init__(self, name="Unnamed Car") -> None:
        self.length = 4  # m
        self.width = 2  # m

        self.color = np.random.rand(3)

        if name == "Unnamed Car":
            self.name, self.color = random_color()
        else:
            self.name = name
        self.x = 0
        self.speed = self.initial_normal_speed()

    def move(self, delta_t, road, lane_index) -> None:
        lanes = road.lanes
        # Check if the car can move back to a previous lane
        if lane_index != 0:
            if self.should_move_back(road, lane_index):
                self.move_back(road, lane_index)
                self.maintain_speed(delta_t)
                return

        # Check if the current lane is save
        (lane_save, car_blocking) = self.is_lane_save(lanes[lane_index])
        if lane_save:
            self.maintain_speed(delta_t)
        else:
            # Check if the car can move to a higher lane
            if self.should_overtake(road, lane_index):
                self.overtake(road, lane_index)
                self.speed = self.speed * 1.2  # Increase speed after overtaking
                self.maintain_speed(delta_t)
                return
            else:
                self.speed = car_blocking.speed
                self.maintain_speed(delta_t)
                return

    def maintain_speed(self, delta_t) -> None:
        self.x += delta_t * self.speed
        self.speed = self.calculate_new_speed()

    def should_overtake(self, road, lane_index) -> bool:
        print("------Overtake Check----------------")
        # Check if it is possible to move to a higher lane
        if lane_index == road.num_of_lanes - 1:
            return False

        # Check if the current lane is save, if it is there is no need to overtake
        (lane_save, car_blocking) = self.is_lane_save(road.lanes[lane_index])
        if lane_save:
            return False

        # Check if the next lane is save, if it is overtake if not do not overtake
        (next_lane_save, next_car_blocking) = self.is_lane_save(
            road.lanes[lane_index + 1]
        )
        if next_lane_save:
            print(f"{self.name} should overtake {car_blocking.name}")
            return True

        else:
            return False

    def overtake(self, road, lane_index) -> None:
        # First check if the car can move to a higher lane (does not check if the lane is save)
        if lane_index == road.num_of_lanes - 1:
            pass
        # Move the car to the next lane
        road.move_vehicle_to_lane(self, lane_index, lane_index + 1)

    def should_move_back(self, road, lane_index) -> bool:
        print("------Move Back Check----------------")
        # Check if it is possible to move to a previous lane
        if lane_index == 0:
            return False
        # Check if the previous lane is save, if it is move back if not do not move back
        (previous_lane_save, previous_car_blocking) = self.is_lane_save(
            road.lanes[lane_index - 1]
        )
        if previous_lane_save:
            print(f"{self.name} should move back")
            return True
        else:
            print(
                f"{self.name} should not move back due to {previous_car_blocking.name}"
            )
            return False

    def move_back(self, road, lane_index) -> None:
        # First check if the car can move to a previous lane (does not check if the lane is save)
        if lane_index == 0:
            pass
        # Move the car to the previous lane
        road.move_vehicle_to_lane(self, lane_index, lane_index - 1)

    def is_lane_save(self, lane) -> tuple[bool, Self or None]:
        # Checks if the lane is save for the car to drive on
        # Distance according to the 2 second rule
        save_distance = 1 * self.speed
        for car in lane:
            if car == self:
                break
            if car.x < self.x + save_distance and car.x > self.x:
                print(
                    f"The lane is not save for {self.name} due to the following car: {car.name}"
                )
                print(f"Distance: {car.x - self.x:.2f} m")
                return (False, car)
        return (True, None)

    def initial_normal_speed(self) -> float:
        mu = 100 / 3.6  # m/s
        sigma = 15 / 3.6  # m/s
        return np.random.default_rng().normal(mu, sigma)

    def calculate_new_speed(self) -> float:
        mu = self.speed  # m/s
        sigma = 5 / 3.6  # m/s
        new_speed = np.random.default_rng().normal(mu, sigma)
        if new_speed < 0:
            return 0
        else:
            return new_speed

    def __str__(self) -> str:
        return f"Car(name={self.name}, x={self.x:.2f} m, speed={self.speed:.2f} m/s or {self.speed * 3.6:.2f} km/h)"

    def graphical_representation(self, y) -> Rectangle:
        x1 = self.x - self.length / 2
        y1 = y - self.width / 2
        return Rectangle(
            (x1, y1),
            self.length,
            self.width,
            linewidth=1,
            edgecolor=self.color,
            facecolor="none",
        )


def spawn_car(road):
    # If called there is a chance that a car will spawn on the road
    # on a random lane at x=0 m where the first lane has a higher probability of spawning a car than the last lane
    # The probability of spawning a car is lamda 1/10 by a poisson distribution per lane

    # First create a list of probabilities per lane make sure they sum to one
    probabilities = []
    for lane_index in range(road.num_of_lanes):
        # Reversed triangular numbers based on the lane index and the number of lanes
        total = (((road.num_of_lanes - 1) ** 2) + (road.num_of_lanes - 1)) / (2)
        reversed_range = list(range(road.num_of_lanes))
        reversed_range.reverse()
        probability = reversed_range[lane_index] / total
        probabilities.append(probability)

    # Next check if a car will spawn on the road by a poisson distribution
    if np.random.default_rng().poisson((1 / 20) * road.num_of_lanes):
        # If a car will spawn, select a lane
        lane_index = np.random.choice(range(road.num_of_lanes), p=probabilities)
        # Create a car
        car = Car()
        # Add the car to the road
        road.add_car(car, lane_index=lane_index)
        # check if lane is save
        (lane_save, car_blocking) = car.is_lane_save(road.lanes[lane_index])
        if not lane_save:
            road.remove_car(car, lane_index=lane_index)


def spawn_car_on_first_lane(road):
    # If called there is a chance that a car will spawn on the road
    # on the first lane at x=0 m
    # The probability of spawning a car is lamda 1/10 by a poisson distribution

    # First check if a car will spawn on the road by a poisson distribution
    if np.random.default_rng().poisson(1 / 5):
        # Create a car
        car = Car()
        # Add the car to the road
        road.add_car(car, lane_index=0)
        # check if lane is save
        (lane_save, car_blocking) = car.is_lane_save(road.lanes[0])
        if not lane_save:
            road.remove_car(car, lane_index=0)


def main() -> None:
    results = np.array([])
    delta_t = 0.1  # s

    road1 = Road(length=200, num_of_lanes=3)

    fig = plt.figure()
    ax = plt.axes(
        xlim=(0, road1.length), ylim=(0, road1.num_of_lanes * road1.lane_width)
    )
    ax.set_aspect("equal")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Lane")
    ax.set_title("Traffic simulation")

    def update(frame_number):
        fig.clear()
        spawn_car_on_first_lane(road1)
        if road1.cars_on_road():
            road1.move_cars(delta_t=delta_t)
            road1.show_graphical_representation()
            plt.draw()

    # Construct the animation, using the update function as the animation director.
    anim = FuncAnimation(fig, update, 10, interval=5)
    # anim.save("tmp/animation.mp4", writer="PillowWriter", fps=1)
    plt.show()

    # for i in tqdm(range(1000)):
    #     t = 0  # s
    #     delta_t = 1  # s

    #     road1 = Road(length=5000, num_of_lanes=1)
    #     car1 = Car()
    #     car2 = Car()
    #     road1.add_car(car1, lane_index=0)
    #     road1.add_car(car2, lane_index=0)

    #     for car in road1.lanes[0]:
    #         while car.x < road1.length:
    #             t += delta_t
    #             car.move(delta_t=delta_t)

    #     results = np.append(results, t)

    # min = np.min(results)
    # print(f"Minimum travel time: {min:.2f} s or {min / 60:.2f} min")
    # max = np.max(results)
    # print(f"Maximum travel time: {max:.2f} s or {max / 60:.2f} min")
    # bins = np.arange(min, max, 5)
    # plt.hist(results, bins=bins)
    # plt.title("Travel times")
    # plt.show()


if __name__ == "__main__":
    main()
