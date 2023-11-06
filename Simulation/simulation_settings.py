# type: ignore
def parse_simulation_settings(
    simulation_settings,
    road_settings,
    lane_distribution,
    spawn_settings,
    vehicle_settings,
):
    """
    Parse the simulation settings to a dictionary.
    """
    simulation = {
        "name": {
            "id": simulation_settings[0],
            "description": simulation_settings[1],
        },
        "road": {
            "length": road_settings[0],
            "lanes": road_settings[1],
        },
        "simulation": {
            "time_step": simulation_settings[3],
            "duration": simulation_settings[2],
        },
        "spawn": {
            "process": spawn_settings[0],
            "cars_per_second": spawn_settings[1],
        },
        "vehicle": {
            "behavior": vehicle_settings[0],
            "behavior_settings": vehicle_settings[1],
            "length": vehicle_settings[2],
        },
        "lane_distribution": lane_distribution,
    }
