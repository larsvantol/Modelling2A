# Write a main loop
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
from tqdm import tqdm


class Road:
    def __init__(self, length, num_of_lanes) -> None:
        # length: length of the road in meters
        # num_of_lanes: number of lanes on the road
        self.length = length
        self.num_of_lanes = num_of_lanes
        self.lanes = {i: [] for i in range(num_of_lanes)}

    def add_car(self, car, lane_index) -> None:
        # Adds a car to the road on the lane given the lane_index
        self.lanes[lane_index].append(car)

    def remove_car(self, car, lane_index) -> None:
        # Removes a car from the road on the lane given the lane_index
        if car in self.lanes[lane_index]:
            self.lanes[lane_index].remove(car)
            print(f"Car {car.name} has left the road")

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
                car.move(delta_t=delta_t, lanes=self.lanes, lane_index=lane_index)
                if car.x > self.length:
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
        lane_width = 5  # m

        # First loop over all cars and plot them on the middle of the lane
        for lane_index in range(self.num_of_lanes):
            for car in self.lanes[lane_index]:
                square = car.graphical_representation(y=(lane_index + 0.5) * lane_width)
                plt.gca().add_patch(square)

        # Next loop over all lanes and plot them
        for lane_index in range(self.num_of_lanes):
            plt.plot(
                [0, self.length],
                [lane_index * lane_width, lane_index * lane_width],
                "k",
            )
        plt.plot(
            [0, self.length],
            [(lane_index + 1) * lane_width, (lane_index + 1) * lane_width],
            "k",
        )


class Car:
    def __init__(self, name="Unnamed Car") -> None:
        self.name = name
        self.x = 0
        self.speed = self.initial_normal_speed()

        self.length = 4  # m
        self.width = 2  # m

        self.color = np.random.rand(3)

    def move(self, delta_t, lanes, lane_index) -> None:
        if self.is_lane_save(lanes[lane_index]):
            self.x += delta_t * self.speed
            self.speed = self.calculate_new_speed()

    def is_lane_save(self, lane) -> bool:
        # Checks if the lane is save for the car to drive on
        # Distance according to the 2 second rule
        save_distance = 2 * self.speed
        for car in lane:
            if car == self:
                break
            if car.x < self.x + save_distance:
                print("not save")
                return False
        return True

    def initial_normal_speed(self) -> float:
        mu = 100 / 3.6  # m/s
        sigma = 5 / 3.6  # m/s
        return np.random.default_rng().normal(mu, sigma)

    def calculate_new_speed(self) -> float:
        mu = self.speed  # m/s
        sigma = 1 / 3.6  # m/s
        return np.random.default_rng().normal(mu, sigma)

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


def main() -> None:
    results = np.array([])
    delta_t = 0.1  # s

    road1 = Road(length=200, num_of_lanes=2)
    car1 = Car("a")
    road1.add_car(car1, lane_index=0)
    car2 = Car("b")
    road1.add_car(car2, lane_index=0)
    road1.move_cars(delta_t=delta_t)
    road1.move_cars(delta_t=delta_t)
    road1.move_cars(delta_t=delta_t)
    car3 = Car("c")
    car3.speed = 130 / 3.6  # m/s
    road1.add_car(car3, lane_index=1)
    # while road1.cars_on_road():
    #     road1.move_cars(delta_t=delta_t)
    #     road1.show_graphical_representation()
    # road1.show_graphical_representation()

    fig = plt.figure()
    # ax = fig.add_axes([0, 0, 1, 1], frameon=False)
    # ax.set_xlim(0, 1), ax.set_xticks([])
    # ax.set_ylim(0, 1), ax.set_yticks([])

    def update(frame_number):
        fig.clear()
        if road1.cars_on_road():
            road1.move_cars(delta_t=delta_t)
            road1.show_graphical_representation()
            plt.draw()

    # Construct the animation, using the update function as the animation director.
    anim = FuncAnimation(fig, update, 10)
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
