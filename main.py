"""Main file for the program."""
from GUI.main_window import MainApplication
from simulation import simulate

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
