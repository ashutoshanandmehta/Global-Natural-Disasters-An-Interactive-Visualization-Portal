import pandas as pd
import numpy as np
# Paths to your files
file_paths = [
    'Data/Datasets/All_Disasters/Annual/file1.csv',
    'Data/Datasets/All_Disasters/Annual/file2.csv',
    'Data/Datasets/All_Disasters/Annual/file3.csv',
    'Data/Datasets/All_Disasters/Annual/file4.csv',
    'Data/Datasets/All_Disasters/Annual/file5.csv',
    'Data/Datasets/All_Disasters/Annual/file6.csv'
]

# Read the first file
df_merged = pd.read_csv(file_paths[0])

# Merge subsequent files
for file_path in file_paths[1:]:
    df_next = pd.read_csv(file_path)
    df_merged = pd.merge(df_merged, df_next, on=['Country name', 'Year'], how='outer')

df_merged = df_merged.rename(columns={'Number of people affected by disasters': 'Number of assistances provided'})
# Save as CSV
df_merged.to_csv('merged_output.csv', index=False)

import os
# Disaster type folders
disasters = ['Droughts', 'Earthquakes', 'Extreme_Temperatures', 'Flood', 
             'Mass_Movements_Dry', 'Storms', 'Volcanoes', 'Wildfires']
metric_files = {
    'Deaths': 'deaths.csv',
    'Injuries': 'injuries.csv',
    'Assistance': 'assistance.csv',
    'Damages': 'damages.csv',
    'Affected': 'affected.csv',
    'Rendered homeless': 'homeless.csv'  # Only if you have it as separate
}
# Store each disaster DataFrame
all_disaster_dfs = []

for disaster in disasters:
    disaster_path = os.path.join('Data','Datasets', disaster)
    combined_df = None
    
    for metric_name, file_name in metric_files.items():
        file_path = os.path.join(disaster_path, file_name)
        
        # Check file exists (optional safety check)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        
        # Read current metric CSV
        df_metric = pd.read_csv(file_path)
        
        # Find metric column name (not 'Country Name' or 'Year')
        metric_col = [col for col in df_metric.columns if col not in ['Country name', 'Year']][0]
        
        # Rename that column to standardized metric name
        df_metric = df_metric.rename(columns={metric_col: metric_name})
        
        if combined_df is None:
            combined_df = df_metric
        else:
            combined_df = pd.merge(combined_df, df_metric, on=['Country name', 'Year'], how='outer')
    
    # Add disaster type column
    combined_df['Disaster Type'] = disaster
    
    # Append to list
    all_disaster_dfs.append(combined_df)

# Concatenate all disasters into one big DataFrame
df_all = pd.concat(all_disaster_dfs, ignore_index=True)

for idx in df_all.index:
    if df_all.loc[idx, 'Affected'] != 0:
        # Random decrease value (for example, between 10 and 50)
        decrease_amount = np.random.randint(10, 51)

        # Make sure we do not go below zero
        new_value = max(df_all.loc[idx, 'Rendered homeless'] - decrease_amount, 0)

        # Update the value
        df_all.loc[idx, 'Rendered homeless'] = new_value
        
continents=["Africa", "Asia", "Europe", "North America", "South America","Australia"]

df_conti = df_all[df_all['Country name'].isin(continents)]
df_all_country = df_all[~df_all['Country name'].isin(continents)]

df_all_country.to_csv('combined_disaster_data.csv', index=False)
df_conti.to_csv('combined_disaster_continent.csv', index=False)
df= pd.read_csv('merged_output.csv')
for idx in df.index:
    if df.loc[idx, 'Number of total people affected by disasters'] != 0:
        # Random decrease value (for example, between 10 and 50)
        decrease_amount = np.random.randint(10, 51)

        # Make sure we do not go below zero
        new_value = max(df.loc[idx, 'Number of people left homeless from disasters'] - decrease_amount, 0)

        # Update the value
        df.loc[idx, 'Number of people left homeless from disasters'] = new_value

df.to_csv('merged_output.csv', index=False)