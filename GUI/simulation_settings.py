"""
This script is used to display the simulation settings in a GUI.
"""
import json
import tkinter as tk
from tkinter import ttk

from Analysis.OpenSimulation import open_simulation


class JSONViewerApp:
    """
    A simple GUI application for displaying JSON data.
    """

    def __init__(self, json_file_path: str | None = None):
        self.root = tk.Tk()
        self.root.title("Simulation Settings")

        # Create a Frame for displaying JSON data
        self.frame = ttk.Frame(self.root)
        self.frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Create a Text widget for displaying JSON content
        self.text_widget = tk.Text(self.frame, wrap=tk.WORD)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a Scrollbar for the Text widget
        self.scrollbar = ttk.Scrollbar(self.frame, command=self.text_widget.yview)  # type: ignore
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        # Load and display JSON data
        self.load_json_data(json_file_path)  # Replace with your JSON file path

    def load_json_data(self, json_file_path: str | None) -> None:
        """
        Load and display JSON data in the Text widget.
        """
        if json_file_path is None:
            json_file_path, _, _ = open_simulation(preference_file="simulation_settings.json")

        try:
            # Load JSON data from the file
            with open(json_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Format JSON data as a string and display it in the Text widget
            formatted_json = json.dumps(data, indent=4)
            self.text_widget.insert(tk.END, formatted_json)

            # Make the Text widget read-only
            self.text_widget.config(state=tk.DISABLED)

        except FileNotFoundError:
            self.text_widget.insert(tk.END, "File not found.")
            self.text_widget.config(state=tk.DISABLED)

    def mainloop(self) -> None:
        """
        Start the GUI application.
        """
        self.root.mainloop()


def show_simulation_settings(json_file_path: str | None) -> None:
    """
    Display the simulation settings in a GUI.
    """
    app = JSONViewerApp(json_file_path)
    app.mainloop()


if __name__ == "__main__":
    show_simulation_settings(json_file_path=None)
