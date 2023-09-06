# Write a main loop
import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm


class Car:
    def __init__(self):
        self.x = 0
        self.speed = self.initial_normal_speed()

    def move(self, delta_t):
        self.x += delta_t * self.speed
        self.speed = self.calculate_new_speed()

    def initial_normal_speed(self):
        mu = 100 / 3.6  # m/s
        sigma = 5 / 3.6  # m/s
        return np.random.default_rng().normal(mu, sigma)

    def calculate_new_speed(self):
        mu = self.speed  # m/s
        sigma = 1 / 3.6  # m/s
        return np.random.default_rng().normal(mu, sigma)

    def __str__(self) -> str:
        return f"Car(x={self.x:.2f} m, speed={self.speed:.2f} m/s or {self.speed * 3.6:.2f} km/h)"


def main():
    results = np.array([])

    for i in tqdm(range(1000)):
        t = 0  # s
        delta_t = 1  # s
        car1 = Car()

        while car1.x < 5000:
            t += delta_t
            car1.move(delta_t=delta_t)

        results = np.append(results, t)

    min = np.min(results)
    print(f"Minimum travel time: {min:.2f} s or {min / 60:.2f} min")
    max = np.max(results)
    print(f"Maximum travel time: {max:.2f} s or {max / 60:.2f} min")
    bins = np.arange(min, max, 5)
    plt.hist(results, bins=bins)
    plt.title("Travel times")
    plt.show()


if __name__ == "__main__":
    main()
