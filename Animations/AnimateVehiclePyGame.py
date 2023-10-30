# type: ignore
"""File that contains the function to show an animation of the simulation using pygame."""
import random

import numpy as np
import numpy.typing as npt
import pandas as pd
import pygame

from Analysis.OpenSimulation import open_simulation


def show_animation():
    """
    This function shows an animation of the simulation using pygame.
    """
    ##################################

    print("Opening simulation...")

    path, _, simulation_settings = open_simulation(preference_file="vehicle_data.csv")

    ##################################

    print("Reading data...")

    # Read the data from the file, ignore the first row which is a header
    data: pd.DataFrame = pd.read_csv(path, header=0)

    # Check if data is empty if so raise an error
    if len(data) == 0:
        raise ValueError(f"Data {data} is empty.")

    ##################################

    # Initialize pygame
    pygame.init()

    # Set screen size
    screen_width = 1200
    screen_height = 600

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Simulation Animation")

    x_left_offset = 15
    x_right_offset = 15
    y_top_offset = 75
    y_bottom_offset = 50

    road_width = screen_width - x_left_offset - x_right_offset
    road_height = screen_height - y_top_offset - y_bottom_offset

    # Calculate multiplier to scale the road to the screen
    x_multiplier: float = road_width / float(simulation_settings["road"]["length"])
    y_multiplier: float = road_height / int(simulation_settings["road"]["lanes"])

    # Define colors
    background_color = (255, 255, 255)
    road_color = (128, 128, 128)
    black_color = (0, 0, 0)

    # Get time step
    time_step = simulation_settings["simulation"]["time_step"]

    car_length = 1.5 * x_multiplier  # m * multiplier

    vehicles_rectangles: dict[int, pygame.Rect] = {}
    vehicles_colors: dict[int, pygame.Color] = {}

    def get_random_color() -> pygame.Color:
        return pygame.Color("#" + "".join([random.choice("0123456789ABCDEF") for _ in range(6)]))

    def map_lane_index(lane_index: int) -> int:
        """This function maps the lane index to the y position on the screen."""

        return simulation_settings["road"]["lanes"] - lane_index - 1

    def draw_lanes() -> None:
        screen.fill(background_color)
        for lane_index in range(simulation_settings["road"]["lanes"]):
            y_lane = map_lane_index(lane_index) * y_multiplier + y_top_offset

            pygame.draw.rect(
                screen,
                road_color,
                (
                    (0 + x_left_offset, y_lane),
                    (road_width, 1 * y_multiplier),
                ),
                0,
            )
            pygame.draw.rect(
                screen,
                black_color,
                (
                    (0 + x_left_offset, y_lane),
                    (road_width, 1 * y_multiplier),
                ),
                1,
            )

    def draw_axis() -> None:
        # This function draws an axis underneath the road with the distance in meters
        tick_size = 100
        ticks: npt.NDArray[np.float_] = np.arange(
            0, float(simulation_settings["road"]["length"]) + tick_size, tick_size
        )
        for tick in ticks:
            tick_position = (
                tick * x_multiplier + x_left_offset,
                y_top_offset + road_height,
            )
            pygame.draw.line(
                screen,
                black_color,
                (tick_position),
                (tick_position[0], tick_position[1] + 5),
                1,
            )
            text = pygame.font.SysFont("Arial", 12).render(f"{tick:.0f}", True, black_color)
            text_rect = text.get_rect(center=(tick_position[0], tick_position[1] + 15))
            screen.blit(text, text_rect.move(0, 5))

    def draw_title() -> None:
        # This function draws the title of the animation
        text = pygame.font.SysFont("Arial", 20).render(
            f"Simulation of {simulation_settings['road']['lanes']} lanes for {simulation_settings['simulation']['duration'] / 60:.0f} minutes with {simulation_settings['spawn']['cars_per_second']:.1f} cars per second.",
            True,
            black_color,
        )
        text_rect = text.get_rect(center=(screen_width / 2, 20))
        screen.blit(text, text_rect)

    def draw_time(time: float) -> None:
        # This function draws the time in the top right corner
        minutes = int(time / 60)
        seconds = time % 60

        text = pygame.font.SysFont("Arial", 15).render(
            f"{minutes:02.0f}:{seconds:04.1f}", True, black_color
        )
        text_rect = text.get_rect(center=(screen_width / 2, 40))
        screen.blit(text, text_rect)

    def draw_information(paused: bool, reverse: bool, speed: float) -> None:
        # This function draws the information in the upper left corner underneath each other
        text = pygame.font.SysFont("Arial", 15).render(f"Paused: {paused}", True, black_color)
        screen.blit(text, (x_left_offset, 5))

        text = pygame.font.SysFont("Arial", 15).render(f"Reversed: {reverse}", True, black_color)
        screen.blit(text, (x_left_offset, 25))

        text = pygame.font.SysFont("Arial", 15).render(f"Speed: {speed:.4f}x", True, black_color)
        screen.blit(text, (x_left_offset, 45))

    def draw_framenum(frame_num: int, total_frames: int) -> None:
        # This function draws the frame number in the top right corner
        text = pygame.font.SysFont("Arial", 15).render(
            f"Frame: {frame_num} / {total_frames}", True, black_color
        )
        screen.blit(text, (screen_width - x_right_offset - 150, 5))

    def update(frame: int) -> None:
        frame_vehicle_data: pd.DataFrame = data[data["time"] == frame]

        # Delete vehicles that are not in the frame
        for vehicle_id in list(vehicles_rectangles.keys()):
            if vehicle_id not in frame_vehicle_data["vehicle_id"].values:
                del vehicles_rectangles[vehicle_id]

        # Draw vehicles
        for _, vehicle_data in frame_vehicle_data.iterrows():
            vehicle_id: int = vehicle_data["vehicle_id"]

            x_left: float = (vehicle_data["position"] - car_length) * x_multiplier + x_left_offset
            y_top: float = (
                map_lane_index(vehicle_data["lane_index"]) + 0.25
            ) * y_multiplier + y_top_offset

            if vehicle_id not in vehicles_rectangles:
                vehicles_rectangles[vehicle_id] = pygame.Rect(
                    x_left,
                    y_top,
                    max(1, car_length * x_multiplier),
                    0.5 * y_multiplier,
                )
                if vehicle_id not in vehicles_colors:
                    vehicles_colors[vehicle_id] = get_random_color()
            else:
                vehicles_rectangles[vehicle_id].left = x_left
                vehicles_rectangles[vehicle_id].top = y_top

            color = vehicles_colors[vehicle_id]

            pygame.draw.rect(screen, color, vehicles_rectangles[vehicle_id], 2)

    frames: npt.NDArray[np.float_] = np.unique(data["time"])

    running = True
    paused = False
    reverse = False
    speed = 1

    frame_num = 0
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Check if the user pressed a key
            if event.type == pygame.KEYDOWN:
                # Check if the user pressed the spacebar
                if event.key == pygame.K_ESCAPE:
                    frame_num = 0
                    paused = False
                    reverse = False
                    speed = 1
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_r or event.key == pygame.K_LEFT:
                    reverse = True
                if event.key == pygame.K_f or event.key == pygame.K_RIGHT:
                    reverse = False
                if event.key == pygame.K_DOWN:
                    speed /= 1.1
                    if speed < 0.0001:
                        speed = 0.0001
                if event.key == pygame.K_UP:
                    speed *= 1.1
                    if speed > 100:
                        speed = 100
                if event.key == pygame.K_LEFTBRACKET:
                    # Skip 10% frames back
                    decrease = int(len(frames) * 0.1)
                    if frame_num - decrease < 0:
                        # If the frame number is smaller than 0 loop back
                        # to the end minus the decrease that is left
                        frame_num = len(frames) - (decrease - frame_num)
                    else:
                        frame_num -= decrease
                if event.key == pygame.K_RIGHTBRACKET:
                    # Skip 10% frames forward
                    increase = int(len(frames) * 0.1)
                    if frame_num + increase >= len(frames):
                        # If the frame number is larger than the number of frames
                        # loop back to the beginning plus the increase that is left
                        frame_num = increase - (len(frames) - frame_num)
                    else:
                        frame_num += increase
                if event.key == pygame.K_COMMA:
                    # Skip 10 frames back
                    if frame_num - 10 < 0:
                        # If the frame number is smaller than 0 loop back
                        # to the end minus the decrease that is left
                        frame_num = len(frames) - (10 - frame_num)
                    else:
                        frame_num -= 10
                if event.key == pygame.K_PERIOD:
                    # Skip 10 frames forward
                    if frame_num + 10 >= len(frames):
                        # If the frame number is larger than the number of frames
                        # loop back to the beginning plus the increase that is left
                        frame_num = 10 - (len(frames) - frame_num)
                    else:
                        frame_num += 10
                if event.key == pygame.K_PAGEUP:
                    if frame_num + 1 >= len(frames):
                        # If the frame number is larger than the number of frames
                        # loop back to the beginning plus the increase that is left
                        frame_num = 1 - (len(frames) - frame_num)
                    else:
                        frame_num += 1
                if event.key == pygame.K_PAGEDOWN:
                    if frame_num - 1 < 0:
                        # If the frame number is smaller than 0 loop back
                        # to the end minus the decrease that is left
                        frame_num = len(frames) - (1 - frame_num)
                    else:
                        frame_num -= 1
                if event.key == pygame.K_r:
                    paused = False
                    reverse = False
                    speed = 1

        draw_lanes()
        draw_title()
        draw_time(frames[frame_num])
        draw_information(paused, reverse, speed)
        draw_framenum(frame_num, len(frames))
        draw_axis()
        # Update and draw
        update(frames[frame_num])
        # Update screen
        pygame.display.flip()

        if not paused:
            if reverse:
                frame_num -= 1
            else:
                frame_num += 1
            if frame_num >= len(frames):
                frame_num = 0

        # Wait
        pygame.time.wait(int(time_step * 1000 / speed))

    pygame.quit()
