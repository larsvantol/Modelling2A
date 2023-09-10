from typing import Self
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
from colors import random_color
import time
from scipy.stats import poisson, norm, expon, lognorm
from scipy.optimize import curve_fit
import os


class Road:
    def __init__(self, length, num_of_lanes) -> None:
        # length: length of the road in meters
        # num_of_lanes: number of lanes on the road
        self.length = length
        self.num_of_lanes = num_of_lanes
        self.lanes = {i: [] for i in range(num_of_lanes)}
        self.lane_width = 5  # m

        self.data = []

    def add_car(self, car, lane_index) -> None:
        # Adds a car to the road on the lane given the lane_index
        self.lanes[lane_index].append(car)
        # print(f"Car {car.name} has entered the road on lane {lane_index}")

    def remove_car(self, car, lane_index) -> None:
        # Removes a car from the road on the lane given the lane_index
        if car in self.lanes[lane_index]:
            self.lanes[lane_index].remove(car)
            # print(f"Car {car.name} has left the road")
            # If the car is removed from the road, add the travel time to the data check if the car is not on x=0
            if car.x != 0:
                self.data.append(sim_time - car.start_time)
                # print(f"Travel time of {car.name}: {sim_time - car.start_time:.2f} s")
                # print(f"Average travel time: {np.mean(self.data):.2f} s")

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

        self.save_space_time = np.random.default_rng().normal(
            2, 0.5
        )  # s (2 second rule)

        self.start_time = sim_time
        self.logging = False

    def print_log(self, log) -> None:
        if self.logging:
            print(log)

    def move(self, delta_t, road, lane_index) -> None:
        lanes = road.lanes
        # Check if the car can move back to a previous lane
        if lane_index != 0:
            if self.should_move_back(road, lane_index):
                self.move_back(road, lane_index)
                self.maintain_speed(delta_t)
                return

        # Check if the current lane is save
        (lane_save, car_blocking) = self.is_lane_save_in_front(lanes[lane_index])
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
        self.print_log(f"{self.name} is maintaining speed")
        self.x += delta_t * self.speed
        self.speed = self.calculate_new_speed()

    def should_overtake(self, road, lane_index) -> bool:
        self.print_log(f"{self.name} is checking if it should overtake")
        # Check if it is possible to move to a higher lane
        if lane_index == road.num_of_lanes - 1:
            return False

        # Check if the current lane is save, if it is there is no need to overtake
        (lane_save, car_blocking) = self.is_lane_save_in_front(road.lanes[lane_index])
        if lane_save:
            return False

        # Check if the next lane is save, if it is overtake if not do not overtake
        (next_lane_save_front, next_car_blocking_front) = self.is_lane_save_in_front(
            road.lanes[lane_index + 1]
        )
        (next_lane_save_behind, next_car_blocking_behind) = self.is_lane_save_behind(
            road.lanes[lane_index + 1]
        )
        if next_lane_save_front and next_lane_save_behind:
            self.print_log(f"{self.name} should overtake {car_blocking.name}")
            return True

        else:
            return False

    def overtake(self, road, lane_index) -> None:
        self.print_log(f"{self.name} is overtaking")
        # First check if the car can move to a higher lane (does not check if the lane is save)
        if lane_index == road.num_of_lanes - 1:
            pass
        # Move the car to the next lane
        road.move_vehicle_to_lane(self, lane_index, lane_index + 1)

    def should_move_back(self, road, lane_index) -> bool:
        self.print_log(f"{self.name} is checking if it should move back")
        # Check if it is possible to move to a previous lane
        if lane_index == 0:
            return False
        # Check if the previous lane is save, if it is move back if not do not move back
        (
            previous_lane_save_front,
            previous_car_blocking_front,
        ) = self.is_lane_save_in_front(road.lanes[lane_index - 1])
        (
            previous_lane_save_behind,
            previous_car_blocking_behind,
        ) = self.is_lane_save_behind(road.lanes[lane_index - 1])
        if previous_lane_save_front and previous_lane_save_behind:
            self.print_log(f"{self.name} should move back")
            return True
        else:
            previous_car_blocking = (
                previous_car_blocking_front
                if previous_car_blocking_front is not None
                else previous_car_blocking_behind
            )
            self.print_log(
                f"{self.name} should not move back due to {previous_car_blocking.name}"
            )
            return False

    def move_back(self, road, lane_index) -> None:
        self.print_log(f"{self.name} is moving back")
        # First check if the car can move to a previous lane (does not check if the lane is save)
        if lane_index == 0:
            pass
        # Move the car to the previous lane
        road.move_vehicle_to_lane(self, lane_index, lane_index - 1)

    def is_lane_save_in_front(self, lane) -> tuple[bool, Self or None]:
        # Checks if the lane is save for the car to drive on
        # Distance according to the 2 second rule
        save_distance = self.save_space_time * self.speed
        for car in lane:
            if car == self:
                break
            if car.x < self.x + save_distance and car.x > self.x:
                self.print_log(
                    f"The lane is not save for {self.name} due to the following car: {car.name}"
                )
                self.print_log(f"Distance: {car.x - self.x:.2f} m")
                return (False, car)
        return (True, None)

    def is_lane_save_behind(self, lane) -> tuple[bool, Self or None]:
        # Checks if the lane is save for the car to drive on
        # Distance according to the 2 second rule
        save_distance = self.save_space_time * self.speed
        for car in lane:
            if car == self:
                break
            if car.x > self.x - save_distance and car.x < self.x:
                self.print_log(
                    f"The lane is not save for {self.name} due to the following car: {car.name}"
                )
                self.print_log(f"Distance: {self.x - car.x:.2f} m")
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


def spawn_car_on_multiple_lanes(road):
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
        (lane_save, car_blocking) = car.is_lane_save_in_front(road.lanes[lane_index])
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
        # Chance that the car is a truck
        if np.random.default_rng().poisson(1 / 5):
            car.length = 10
            car.width = 3
            car.speed = car.initial_normal_speed() * 0.5
        # Add the car to the road
        road.add_car(car, lane_index=0)
        # check if lane is save
        (lane_save, car_blocking) = car.is_lane_save_in_front(road.lanes[0])
        if not lane_save:
            road.remove_car(car, lane_index=0)


def simulate(road, delta_t):
    global sim_time  # Declare sim_time as nonlocal to modify it within the function
    sim_time += delta_t  # Update simulation time as the simulation progresses

    spawn_car_on_first_lane(road)
    if road.cars_on_road():
        road.move_cars(delta_t=delta_t)


def get_stats(road, simulation_time_data):
    stats = dict()
    stats["min_travel_time"] = np.min(road.data)
    stats["max_travel_time"] = np.max(road.data)
    stats["mean_travel_time"] = np.mean(road.data)
    stats["std_dev"] = np.std(road.data)

    bins = np.arange(
        stats["min_travel_time"],
        stats["max_travel_time"],
        (stats["max_travel_time"] - stats["min_travel_time"]) / 50,
    )
    hist, bins = np.histogram(road.data, bins=bins)

    stats["most_common_travel_time"] = bins[np.argmax(hist)]
    stats["amount_of_most_common_travel_time"] = np.argmax(road.data)
    stats["real_time"] = simulation_time_data["real_time"]
    stats["simulation_time"] = simulation_time_data["simulation_time"]
    stats["amount_of_cars"] = len(road.data)
    stats["road_length"] = road.length
    stats["num_of_lanes"] = road.num_of_lanes
    stats["bins"] = bins
    return stats


def print_stats(stats):
    # Print stats using the stats dictionary make sure they are aligned
    print(f"Road length: \t\t{stats['road_length']:.2f} m")
    print(f"Number of lanes: \t{stats['num_of_lanes']}")
    print(
        f"Minimum travel time: \t{stats['min_travel_time']:.2f} s or {stats['min_travel_time'] / 60:.2f} min"
    )
    print(
        f"Maximum travel time: \t{stats['max_travel_time']:.2f} s or {stats['max_travel_time'] / 60:.2f} min"
    )
    print(
        f"Average travel time: \t{stats['mean_travel_time']:.2f} s or {stats['mean_travel_time'] / 60:.2f} min"
    )
    print(
        f"Most common time: \t{stats['most_common_travel_time']:.2f} s or {stats['most_common_travel_time'] / 60:.2f} min"
    )
    print(
        f"Amount most common time: \t{stats['amount_of_most_common_travel_time']} / {stats['amount_of_cars']}"
    )
    print(f"Standard deviation: \t{stats['std_dev']:.2f} s")
    print(f"Amount of cars: \t{stats['amount_of_cars']}")
    print(
        f"Simulation time: \t{stats['simulation_time']:.2f} s or {stats['simulation_time'] / 60:.2f} min"
    )
    print(f"Time to simulate: \t{stats['real_time']:.2f} s")


def plot_travel_times(road, stats):
    # Plot the data of the simulation

    plt.figure(figsize=(10, 6))

    plt.hist(
        road.data,
        bins=stats["bins"],
        density=True,
        label="Simulation data",
        alpha=0.5,
        rwidth=0.9,
        color="b",
    )
    plt.title("Travel times")

    # Also plot a line for the average travel time
    plt.axvline(stats["mean_travel_time"], color="k", linewidth=1)
    plt.text(
        stats["mean_travel_time"] + 0.1,
        0.8 * plt.ylim()[1],
        f"Average travel time: {stats['mean_travel_time']:.2f} s",
    )

    # Also plot a line for the most common travel time
    plt.axvline(stats["most_common_travel_time"], color="k", linewidth=1)
    plt.text(
        stats["most_common_travel_time"] + 0.1,
        0.7 * plt.ylim()[1],
        f"Most common travel time: {stats['most_common_travel_time']:.2f} s",
    )

    # Also plot a line for the standard deviation
    plt.axvline(
        stats["mean_travel_time"] + stats["std_dev"],
        color="k",
        linestyle="dashed",
        linewidth=1,
    )
    plt.text(
        stats["mean_travel_time"] + stats["std_dev"] + 0.1,
        0.6 * plt.ylim()[1],
        f"Standard deviation: {stats['std_dev']:.2f} s",
    )
    plt.axvline(
        stats["mean_travel_time"] - stats["std_dev"],
        color="k",
        linestyle="dashed",
        linewidth=1,
    )

    # Fit some distributions to the data
    x = np.linspace(0, stats["max_travel_time"], 1000)

    # Fit the normal distribution to the histogram
    p = norm.pdf(x, loc=stats["mean_travel_time"], scale=stats["std_dev"])
    plt.plot(x, p, "g", lw=2, label="Fitted Normal Distribution")

    # Fit a poisson distribution to the data
    p = poisson.pmf(x, stats["mean_travel_time"])
    plt.plot(x, p, "b", lw=2, label="Fitted Poisson Distribution")

    # Fit a exponential distribution to the data
    loc, scale = expon.fit(road.data)
    p = expon.pdf(x, loc, scale)
    plt.plot(x, p, "r", label="Fitted Exponential")

    # Fit a exponential distribution to the data for the most common travel time
    filtered_data = list(
        filter(lambda time: time >= stats["most_common_travel_time"], road.data)
    )
    loc, scale = expon.fit(filtered_data)
    p = expon.pdf(x, loc, scale)
    plt.plot(x, p, "r", linestyle="dashed", label="Fitted Exponential")

    # Fit a lognormal distribution to the data
    shape, loc, scale = lognorm.fit(road.data)
    p = lognorm.pdf(x, shape, loc, scale)
    plt.plot(x, p, "y", label="Fitted Lognormal")

    plt.xlabel("Travel time (s)")
    plt.ylabel("Probability density")

    plt.legend()

    plt.show()


def animate(road, delta_t):
    fig = plt.figure()
    ax = plt.axes(xlim=(0, road.length), ylim=(0, road.num_of_lanes * road.lane_width))
    ax.set_aspect("equal")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Lane")
    ax.set_title("Traffic simulation")

    def update(frame_number):
        fig.clear()

        global sim_time  # Declare sim_time as nonlocal to modify it within the function

        sim_time += delta_t  # Update simulation time as the simulation progresses

        spawn_car_on_first_lane(road)
        if road.cars_on_road():
            t1 = time.perf_counter_ns()
            road.move_cars(delta_t=delta_t)
            t2 = time.perf_counter_ns()
            # print(f"Time to move cars: {t2} - {t1} = {(t2 - t1) / 1e6:.2f} ms")
        # print("frame_number:", frame_number)
        road.show_graphical_representation()
        # Add time to the plot
        plt.text(
            0.8 * plt.xlim()[1],
            0.9 * plt.ylim()[1],
            f"Time: {sim_time:.2f} s",
            fontsize=12,
        )
        # plt.draw()

    # Construct the animation, using the update function as the animation director.
    anim = FuncAnimation(fig=fig, func=update, frames=400, interval=30)
    filepath = os.path.abspath("tmp/animation.html")
    anim.save(filename=filepath, writer="html")

    # open the file
    os.startfile(filepath)


def run_simulation(road, delta_t):
    start_time_of_simulation = time.perf_counter_ns()

    for _ in tqdm(range(100000)):
        simulate(road, delta_t)

    end_time_of_simulation = time.perf_counter_ns()
    simulation_time_data = {
        "real_time": (end_time_of_simulation - start_time_of_simulation) / 1e9,
        "simulation_time": sim_time,
    }

    stats = get_stats(road, simulation_time_data)
    print_stats(stats)
    plot_travel_times(road, stats)


def main() -> None:
    delta_t = 0.1  # s

    global sim_time  # Declare sim_time as a global variable
    sim_time = 0  # Initialize simulation time

    road1 = Road(length=500, num_of_lanes=3)

    # animate(road1, delta_t)
    run_simulation(road1, delta_t)


if __name__ == "__main__":
    main()
