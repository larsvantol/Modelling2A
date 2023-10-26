import bisect


def close_vehicles(vehicles, position):
    if len(vehicles) == 0:
        return (None, None)

    index = bisect.bisect_left(vehicles, -position, key=lambda v: -v.position)
    return index


class V:
    def __init__(self, position):
        self.position = position

    def __repr__(self):
        return f"V({self.position})"


if __name__ == "__main__":
    vehicles = [V(4), V(3), V(2), V(1)]

    bisect.insort(vehicles, V(2.5), key=lambda v: -v.position)
    print(vehicles)
