import getGoogleSheetsData
import os
import pandas as pd
from datetime import datetime

localSavePath = getGoogleSheetsData.main()
formatted_date = datetime.now().strftime("%m_%d_%Y")



# Read the CSV file into a DataFrame
df = pd.read_csv(localSavePath, header=None)


# For each GitCloneLink and FolderLocation, push it to github
# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    # Extract the GitCloneLink and FolderLocation from the row
    git_clone_link = row[0]
    folder_location = row[1]

    # Construct the command to push to GitHub
    command = f'git -C "{folder_location}" add . && git -C "{folder_location}" commit -m "Backup {formatted_date}" && git -C "{folder_location}" push {git_clone_link}'
    
    # Execute the command
    os.system(command)





