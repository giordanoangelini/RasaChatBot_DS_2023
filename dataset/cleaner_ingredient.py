import pandas as pd
import numpy as np

data = pd.read_csv("recipe.csv", header=0, sep=',', encoding=None)
data = data['title']
np.savetxt("recipe.txt", data.values, fmt='%s')

file = open(r"recipe.txt", "r")

# Splits each row
lines = file.read().splitlines()
n = 0

# Insert target output path here
file2 = open(r"recipe.yml", "w")

# Writes the headers(?), remember to change the lookup name
file2.write("version: \"3.1\"\nnlu:\n  - lookup: recipe  \n    examples: |\n")

# Adds indent and dash to each line
for line in lines:
    file2.write("      - " + str(line) + "\n")

# Closes the files
file.close()
file2.close()