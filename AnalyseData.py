import os
import csv

folder = "tmp/simple_model/"
filename = "simple_model_2_travel_times.csv"
path = os.path.join(folder, filename)

import pandas as pd

df = pd.read_csv(path, sep=",")
