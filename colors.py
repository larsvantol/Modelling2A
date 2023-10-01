import random


colors = [
    ("red", (1, 0, 0)),
    ("green", (0, 1, 0)),
    ("blue", (0, 0, 1)),
    ("black", (0, 0, 0)),
    ("orange", (1, 0.647, 0)),
    ("yellow", (1, 1, 0)),
    ("purple", (0.502, 0, 0.502)),
    ("pink", (1, 0.753, 0.796)),
    ("brown", (0.647, 0.165, 0.165)),
    ("gray", (0.502, 0.502, 0.502)),
    ("cyan", (0, 1, 1)),
    ("magenta", (1, 0, 1)),
    ("lightblue", (0.678, 0.843, 0.902)),
    ("lightgreen", (0.565, 0.933, 0.565)),
    ("lightpink", (1, 0.714, 0.756)),
    ("lightbrown", (0.804, 0.522, 0.247)),
    ("lightpurple", (0.576, 0.439, 0.859)),
    ("lightorange", (1, 0.8, 0.6)),
]


def random_color():
    return random.choice(colors)


def main():
    print(random_color())


if __name__ == "__main__":
    main()
