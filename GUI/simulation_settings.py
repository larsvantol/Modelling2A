import tkinter as tk
from tkinter import ttk
import json
from Analysis.OpenSimulation import open_simulation


class JSONViewerApp:
    def __init__(self, root, json_file):
        self.root = root
        self.root.title("Simulation Settings")

        # Create a Frame for displaying JSON data
        self.frame = ttk.Frame(root)
        self.frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Create a Text widget for displaying JSON content
        self.text_widget = tk.Text(self.frame, wrap=tk.WORD)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a Scrollbar for the Text widget
        self.scrollbar = ttk.Scrollbar(self.frame, command=self.text_widget.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        # Load and display JSON data
        self.load_json_data(json_file)  # Replace with your JSON file path

    def load_json_data(self, json_file):
        try:
            # Load JSON data from the file
            with open(json_file, "r") as file:
                data = json.load(file)

            # Format JSON data as a string and display it in the Text widget
            formatted_json = json.dumps(data, indent=4)
            self.text_widget.insert(tk.END, formatted_json)

            # Make the Text widget read-only
            self.text_widget.config(state=tk.DISABLED)

        except FileNotFoundError:
            self.text_widget.insert(tk.END, "File not found.")
            self.text_widget.config(state=tk.DISABLED)


def show_simulation_settings_gui():
    root = tk.Tk()
    path, project_folder, SIMULATION_SETTINGS = open_simulation(
        preference_file="simulation_settings.json"
    )
    app = JSONViewerApp(root, path)
    root.mainloop()


if __name__ == "__main__":
    show_simulation_settings_gui()
