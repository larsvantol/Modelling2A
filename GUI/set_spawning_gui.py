# type: ignore
"""
GUI for selecting a lane distribution.
"""
import tkinter as tk
from functools import partial
from tkinter import messagebox, ttk
from typing import Any

# pylint: disable=wrong-import-position
if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.getcwd())
# pylint: enable=wrong-import-position

from Behaviors.Behaviors import BehaviorType, behavior_options
from Spawning.LaneDistributions import LaneDistribution, lane_distributions
from Spawning.Spawners import spawn_process_types


class FloatEntry(tk.Entry):
    """Entry widget that only accepts floats."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        vcmd = (self.register(self.validate), "%P")
        self.config(validate="all", validatecommand=vcmd)

    def validate(self, text: str):
        """Validate the text."""

        return (
            all(char in "0123456789." for char in text)  # only 0-9 and periods
            and text.count(".") <= 1  # only 0 or 1 periods
        )


class IntEntry(tk.Entry):
    """Entry widget that only accepts integers."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        vcmd = (self.register(self.validate), "%P")
        self.config(validate="all", validatecommand=vcmd)

    def validate(self, text: str):
        """Validate the text."""

        return all(char in "0123456789" for char in text)


class StringEntry(tk.Entry):
    """Entry widget that only accepts strings."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        vcmd = (self.register(self.validate), "%P")
        self.config(validate="all", validatecommand=vcmd)

    def validate(self, text: str):
        """Validate the text."""

        return all(
            char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789_#"
            for char in text
        )


class SetSpawningGUI:
    """GUI for selecting a lane distribution."""

    def __init__(self):
        self.set_standard_parameters()
        self.simulation_settings: None | (str, str, float, float) = None
        self.lane_distribution: None | LaneDistribution = None
        self.road_settings: tuple[None, None] | tuple[float, int] = (None, None)
        self.behavior_settings: None | tuple[str, dict[str, dict[str, tk.DoubleVar]]] = None
        self.spawn_settings: tuple[None, None] | tuple[str, float] = (None, None)
        self.vehicle_settings: tuple[None, None, None] | tuple[
            tuple[str, tuple[str, float]], tuple[float, float], float
        ] = (None, None, None)
        self.root = self.create_window()
        self.create_layout()

    def set_standard_parameters(self):
        """Set the standard parameters."""

        self.standard_parameters = {
            "simulation_name": "Simulation Name",
            "simulation_description": "Simulation Description",
            "simulation_duration": 10 * 60 * 60,  # s
            "simulation_delta_t": 0.1,  # s
            "vehicle_length": 1.5,  # m
            "velocity_mu": 100,  # km/h
            "velocity_sigma": 10,  # km/h
            "lanes": 3,
            "road_length": 500,  # m
        }
        self.standard_parameters["spawn_rate"] = round(0.2 * self.standard_parameters["lanes"], 2)

    def create_window(self) -> tk.Tk:
        """Create the window."""
        window = tk.Tk()
        window.title("Select Lane Distribution")
        return window

    def create_layout(self):
        """Create the layout."""

        # Create the simulation settings labelframe

        simulation_settings_labelframe = ttk.LabelFrame(self.root, text="Simulation settings:")
        simulation_settings_labelframe.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        simulation_settings_labelframe.grid_columnconfigure(1, weight=1)

        simulation_name_label = ttk.Label(simulation_settings_labelframe, text="Name:")
        simulation_name_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        simulation_name_var = tk.StringVar(
            self.root, value=self.standard_parameters["simulation_name"]
        )

        simulation_name_entry = ttk.Entry(
            simulation_settings_labelframe, textvariable=simulation_name_var
        )
        simulation_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        simulation_description_label = ttk.Label(
            simulation_settings_labelframe, text="Description:"
        )
        simulation_description_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        simulation_description_var = tk.StringVar(
            self.root, value=self.standard_parameters["simulation_description"]
        )

        simulation_description_entry = ttk.Entry(
            simulation_settings_labelframe, textvariable=simulation_description_var
        )
        simulation_description_entry.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        simulation_duration_label = ttk.Label(simulation_settings_labelframe, text="Duration (s):")
        simulation_duration_label.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        simulation_duration_var = tk.DoubleVar(
            self.root, value=self.standard_parameters["simulation_duration"]
        )

        simulation_duration_entry = FloatEntry(
            simulation_settings_labelframe, textvariable=simulation_duration_var
        )
        simulation_duration_entry.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        simulation_delta_t_label = ttk.Label(simulation_settings_labelframe, text="Δt (s):")
        simulation_delta_t_label.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        simulation_delta_t_var = tk.DoubleVar(
            self.root, value=self.standard_parameters["simulation_delta_t"]
        )

        simulation_delta_t_entry = FloatEntry(
            simulation_settings_labelframe, textvariable=simulation_delta_t_var
        )
        simulation_delta_t_entry.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

        # Create the road settings labelframe

        road_settings_labelframe = ttk.LabelFrame(self.root, text="Road settings:")
        road_settings_labelframe.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        road_length_label = ttk.Label(road_settings_labelframe, text="Road length (m):")
        road_length_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        road_length_var = tk.DoubleVar(self.root, value=self.standard_parameters["road_length"])

        road_length_entry = FloatEntry(road_settings_labelframe, textvariable=road_length_var)
        road_length_entry.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        amount_lanes_label = ttk.Label(road_settings_labelframe, text="Amount of lanes:")
        amount_lanes_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        amount_lanes_var = tk.IntVar(self.root, value=int(self.standard_parameters["lanes"]))

        amount_lanes_entry = IntEntry(road_settings_labelframe, textvariable=amount_lanes_var)
        amount_lanes_entry.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Create the spawning settings labelframe

        spawning_settings_labelframe = ttk.LabelFrame(self.root, text="Spawning settings:")
        spawning_settings_labelframe.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Create the lane distribution labelframe
        # which is a child of the spawning settings labelframe

        distribution_labelframe = ttk.LabelFrame(
            spawning_settings_labelframe, text="Lane distribution:"
        )
        distribution_labelframe.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        lane_distribution_label = ttk.Label(distribution_labelframe, text="Lane distribution:")
        lane_distribution_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        selected_lane_distribution = tk.StringVar(self.root)
        selected_lane_distribution.set(next(iter(lane_distributions)))

        lane_distributions_option_menu = ttk.OptionMenu(
            distribution_labelframe,
            selected_lane_distribution,
            selected_lane_distribution.get(),
            *lane_distributions,
        )
        lane_distributions_option_menu.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Create the spawner labelframe which is a child of the spawning settings labelframe

        spawner_labelframe = ttk.LabelFrame(spawning_settings_labelframe, text="Spawner:")
        spawner_labelframe.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        spawner_label = ttk.Label(spawner_labelframe, text="Spawner type:")
        spawner_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        selected_spawner = tk.StringVar(self.root)
        selected_spawner.set(next(iter(spawn_process_types)))

        spawner_option_menu = ttk.OptionMenu(
            spawner_labelframe, selected_spawner, selected_spawner.get(), *spawn_process_types
        )
        spawner_option_menu.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        spawner_rate_label = ttk.Label(spawner_labelframe, text="Spawn rate (vehicles/s):")
        spawner_rate_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        spawner_rate_var = tk.DoubleVar(self.root, value=self.standard_parameters["spawn_rate"])

        spawner_rate_entry = FloatEntry(spawner_labelframe, textvariable=spawner_rate_var)
        spawner_rate_entry.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Create the vehicle factory labelframe which is a child of the spawning settings labelframe

        vehicle_factory_labelframe = ttk.LabelFrame(
            spawning_settings_labelframe, text="Vehicle factory:"
        )
        vehicle_factory_labelframe.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        vehicle_factory_label = ttk.Label(vehicle_factory_labelframe, text="Behavior:")
        vehicle_factory_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        vehicle_factory_frame = ttk.Frame(vehicle_factory_labelframe)
        vehicle_factory_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        selected_behaviour = tk.StringVar(self.root)
        selected_behaviour.set(next(iter(behavior_options)))

        behaviour_option_menu = ttk.OptionMenu(
            vehicle_factory_frame,
            selected_behaviour,
            next(iter(behavior_options)),
            *behavior_options,
        )
        behaviour_option_menu.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        vehicle_factory_button = ttk.Button(
            vehicle_factory_frame,
            text="Select",
            command=lambda: self.edit_behavior(selected_behaviour.get()),
        )
        vehicle_factory_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        desired_velocity_label = ttk.Label(
            vehicle_factory_labelframe, text="Desired velocity (km/h):"
        )
        desired_velocity_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        desired_velocity_frame = ttk.Frame(vehicle_factory_labelframe)
        desired_velocity_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        desired_velocity_mu_label = ttk.Label(desired_velocity_frame, text="μ:")
        desired_velocity_mu_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        desired_velocity_mu_var = tk.DoubleVar(
            self.root, value=self.standard_parameters["velocity_mu"]
        )

        desired_velocity_mu_entry = FloatEntry(
            desired_velocity_frame, textvariable=desired_velocity_mu_var
        )
        desired_velocity_mu_entry.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        desired_velocity_sigma_label = ttk.Label(desired_velocity_frame, text="σ:")
        desired_velocity_sigma_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        desired_velocity_sigma_var = tk.DoubleVar(
            self.root, value=self.standard_parameters["velocity_sigma"]
        )

        desired_velocity_sigma_entry = FloatEntry(
            desired_velocity_frame, textvariable=desired_velocity_sigma_var
        )
        desired_velocity_sigma_entry.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        vehicle_length_label = ttk.Label(vehicle_factory_labelframe, text="Length (m):")
        vehicle_length_label.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        vehicle_length_var = tk.DoubleVar(
            self.root, value=self.standard_parameters["vehicle_length"]
        )

        vehicle_length_entry = FloatEntry(
            vehicle_factory_labelframe, textvariable=vehicle_length_var
        )
        vehicle_length_entry.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        # Create the run simulation button

        button = ttk.Button(
            self.root,
            text="Run Simulation",
            command=partial(
                self.handle_run_simulation,
                simulation_name=simulation_name_var,
                simulation_description=simulation_description_var,
                simulation_duration=simulation_duration_var,
                simulation_delta_t=simulation_delta_t_var,
                lane_distribution_type=selected_lane_distribution,
                spawner=selected_spawner,
                spawn_rate=spawner_rate_var,
                total_lanes=amount_lanes_var,
                road_length=road_length_var,
                desired_velocity_mu=desired_velocity_mu_var,
                desired_velocity_sigma=desired_velocity_sigma_var,
                vehicle_length=vehicle_length_var,
            ),
        )
        button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def mainloop(self):
        """Run the mainloop."""
        self.root.mainloop()

    def edit_behavior(self, behavior_type: str):
        """Edit the behavior."""
        behavior_gui = SetBehaviorGUI(self, behavior_type)
        behavior_gui.mainloop()

    def handle_run_simulation(
        self,
        simulation_name: tk.StringVar,
        simulation_description: tk.StringVar,
        simulation_duration: tk.DoubleVar,
        simulation_delta_t: tk.DoubleVar,
        lane_distribution_type: tk.StringVar,
        spawner: tk.StringVar,
        spawn_rate: tk.DoubleVar,
        total_lanes: tk.IntVar,
        road_length: tk.DoubleVar,
        desired_velocity_mu: tk.DoubleVar,
        desired_velocity_sigma: tk.DoubleVar,
        vehicle_length: tk.DoubleVar,
    ):
        """Handle a button press."""
        if self.behavior_settings == (None, None):
            # Show error message and return
            messagebox.showerror(title="Error", message="Behavior not selected")  # type: ignore
            return
        self.root.destroy()
        self.simulation_settings = (
            simulation_name.get().replace(" ", "_"),
            simulation_description.get(),
            simulation_duration.get(),
            simulation_delta_t.get(),
        )
        self.road_settings = (road_length.get(), total_lanes.get())
        self.lane_distribution = lane_distribution_type.get()
        self.spawn_settings = (
            spawn_process_types[spawner.get()],
            float(spawn_rate.get()),
        )
        self.vehicle_settings = (
            self.behavior_settings,
            (desired_velocity_mu.get(), desired_velocity_sigma.get()),
            vehicle_length.get(),
        )


class SetBehaviorGUI:
    """GUI for selecting a lane distribution."""

    def __init__(
        self,
        master: SetSpawningGUI,
        behavior_type: str,
    ):
        self.root = self.create_window()
        self.master = master
        self.behavior = behavior_type
        self.create_layout(behavior_type)

    def create_window(self) -> tk.Tk:
        """Create the window."""
        window = tk.Tk()
        window.title("Edit Behavior")
        return window

    def create_layout(self, behavior_type: str):
        """Create the layout."""

        if not behavior_type in behavior_options:
            raise ValueError("Behavior type not found")

        behavior_settings_labelframe = ttk.LabelFrame(
            self.root, text=f"{behavior_type} parameters:"
        )
        behavior_settings_labelframe.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        behavior = behavior_options[behavior_type]

        standard_parameters = behavior.standard_parameters()

        parameters = {
            parameter: {
                "mu": tk.DoubleVar(self.root, value=value),
                "sigma": tk.DoubleVar(self.root, value=0),
            }
            for name, parameter, value, unit in standard_parameters
        }

        parameter_label = ttk.Label(
            behavior_settings_labelframe, text=f"{behavior_type} parameters:"
        )
        parameter_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        value_mu_label = ttk.Label(behavior_settings_labelframe, text="μ:")
        value_mu_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        value_sigma_label = ttk.Label(behavior_settings_labelframe, text="σ:")
        value_sigma_label.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        for index, (name, parameter, value, unit) in enumerate(standard_parameters):
            unit = f"({unit})" if unit != "" else ""
            label = ttk.Label(behavior_settings_labelframe, text=f"{name} {unit}: ")
            label.grid(row=index + 1, column=0, padx=10, pady=10, sticky="nsew")

            entry_mu = FloatEntry(
                behavior_settings_labelframe, textvariable=parameters[parameter]["mu"]
            )
            entry_mu.grid(row=index + 1, column=1, padx=10, pady=10, sticky="nsew")

            entry_sigma = FloatEntry(
                behavior_settings_labelframe, textvariable=parameters[parameter]["sigma"]
            )
            entry_sigma.grid(row=index + 1, column=2, padx=10, pady=10, sticky="nsew")

        button = ttk.Button(
            self.root, text="Set", command=lambda: self.handle_button_press(parameters)
        )
        button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def mainloop(self):
        """Run the mainloop."""
        self.root.mainloop()

    def handle_button_press(self, parameters: dict[str, dict[str, tk.DoubleVar]]):
        """Handle a button press."""
        self.root.destroy()
        parameters_dict = {
            parameter: {
                "mu": parameters[parameter]["mu"].get(),
                "sigma": parameters[parameter]["sigma"].get(),
            }
            for parameter in parameters
        }
        self.master.behavior_settings = (
            self.behavior,
            parameters_dict,
        )


def get_simulation_settings() -> (
    tuple[
        str,
        tuple[float, int],
        str,
        tuple[str, float],
        tuple[tuple[str, tuple[str, float]], tuple[float, float], float],
    ]
):
    """Get the simulation settings using a GUI."""

    gui = SetSpawningGUI()
    gui.mainloop()

    if gui.simulation_settings is None:
        raise ValueError("Lane distribution type not selected")
    if gui.road_settings is None:
        raise ValueError("Road settings not selected")
    if gui.lane_distribution is None:
        raise ValueError("Lane distribution not selected")
    if gui.spawn_settings is None:
        raise ValueError("Spawn settings not selected")
    if gui.vehicle_settings is None:
        raise ValueError("Vehicle settings not selected")

    return gui.simulation_settings, gui.road_settings, gui.lane_distribution, gui.spawn_settings, gui.vehicle_settings  # type: ignore


if __name__ == "__main__":
    (
        simulation_settings,
        road_settings,
        lane_distributions_settings,
        spawn_settings,
        vehicle_settings,
    ) = get_simulation_settings()
    print(simulation_settings)
    print(road_settings)
    print(lane_distributions_settings)
    print(spawn_settings)
    print(vehicle_settings)
