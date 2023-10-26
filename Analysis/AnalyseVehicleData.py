from tkinter.simpledialog import askinteger
from tkinter.filedialog import asksaveasfilename
import pandas as pd
from Analysis.OpenSimulation import open_simulation
import matplotlib.pyplot as plt
import tqdm


def analyse_vehicle_data():
    ##################################

    print("Opening simulation...")

    path, project_folder, SIMULATION_SETTINGS = open_simulation(
        preference_file="vehicle_data.csv"
    )

    ##################################

    print("Reading data...")

    # Read the data from the file, ignore the first row which is a header
    data = pd.read_csv(path, header=0)

    # Check if data is empty if so raise an error
    if len(data) == 0:
        raise ValueError(f"Data {data} is empty.")

    #################################

    vehicle_id = None
    vehicles_ids = data["vehicle_id"].unique()
    min_vehicle_id = min(vehicles_ids)
    max_vehicle_id = max(vehicles_ids)
    while not vehicle_id in data["vehicle_id"].values:
        vehicle_id = askinteger(
            "Vehicle ID",
            f"Enter the ID of the vehicle you want to analyse: \n [{min_vehicle_id} - {max_vehicle_id}]",
        )

    print("Filtering data...")
    # filter data
    data = data[data["vehicle_id"] == vehicle_id]

    #################################

    delta_t = SIMULATION_SETTINGS["simulation"]["time_step"]

    print("Calculating acceleration...")

    def calculate_acceleration(velocity, previous_velocity, time_step):
        return (velocity - previous_velocity) / time_step

    # add previous velocity to data
    data["previous_velocity"] = data["velocity"].shift(1)

    for row in tqdm.tqdm(data.iterrows(), total=len(data)):
        row = row[1]
        data.loc[row.name, "acceleration"] = calculate_acceleration(
            row["velocity"], row["previous_velocity"], delta_t
        )

    print(data)

    #################################

    # shift time steps to start at 0
    time_steps = data["time"].values
    time_steps -= time_steps[0]

    positions = data["position"].values
    velocities = data["velocity"].values
    accelerations = data["acceleration"].values
    lane_changes = data["lane_index"].values

    #################################

    print("Plotting data...")

    # Create a figure with 3 subplots in a column
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
    fig.tight_layout(pad=2.0)

    # Create a line plot of the positions
    ax1.plot(time_steps, positions, label="Position")
    # Create a line plot of the velocities
    ax2.plot(time_steps, velocities, label="Velocity")
    # Create a line plot of the accelerations
    ax3.plot(time_steps, accelerations, label="Acceleration")
    # Create a line plot of the lane changes
    ax4.plot(time_steps, lane_changes, label="Lane changes")

    # Set the title of the figure
    fig.suptitle(f"Vehicle Data: {vehicle_id}")

    # Set the labels of the axes
    ax1.set_ylabel("Position")
    ax2.set_ylabel("Velocity")
    ax3.set_ylabel("Acceleration")
    ax4.set_ylabel("Lane changes")

    ax4.set_xlabel("Time")

    # Show the legend
    ax1.legend(loc="upper right")
    ax2.legend(loc="upper right")
    ax3.legend(loc="upper right")
    ax4.legend(loc="upper right")

    # Tkinter to ask for a file name
    file = asksaveasfilename(
        title="Save vehicle data",
        filetypes=[("PNG", "*.png")],
        defaultextension=".png",
        initialdir=project_folder,
        initialfile=f"vehicle_data_{vehicle_id}.png",
    )
    plt.savefig(
        file,
        dpi=300,
        format="png",
        bbox_inches="tight",
        transparent=False,
    )
    plt.savefig(
        file.replace(".png", "_transparent.png"),
        dpi=300,
        format="png",
        bbox_inches="tight",
        transparent=True,
    )

    # Show the plot
    plt.show()

    #################################


if __name__ == "__main__":
    analyse_vehicle_data()
