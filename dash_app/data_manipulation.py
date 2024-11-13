import os
import pandas as pd

DATA_DIR = "../../data/msdlive-gridcerf/gridcerf"

folders = [os.path.join(DATA_DIR, "common"),
            os.path.join(DATA_DIR, "scenario_specific"),
            os.path.join(DATA_DIR, "technology_specific")
            ]

file_data = []

for folder in folders:

    if os.path.exists(folder):

        for filename in os.listdir(folder):

            file_path = os.path.join(folder, filename)

            if os.path.isfile(file_path):  # Ensure it's a file (not a folder)
                file_path = file_path.replace("../../data/msdlive-gridcerf/", "")
                filename = filename.replace("gridcerf_", "").replace(".tif", "").replace("_", " ")
                file_data.append({"filename": filename, "filepath": file_path})
    else:
        print(f"Folder {folder} does not exist!")

# Create a pandas DataFrame from the list
df = pd.DataFrame(file_data)

# Save the DataFrame as a CSV file
df.to_csv("layer_catalogue.csv", index=False)

print("CSV file has been saved as 'layer_catalogue.csv'.")
