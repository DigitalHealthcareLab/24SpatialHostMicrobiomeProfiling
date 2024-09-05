import pandas as pd
import os

# List of directories containing Bracken output files
directories = [
    "data/processed/DoubleFilter/BS1_NI2/splitted_bracken",
    "data/processed/DoubleFilter/IBD1_I1_NI1/splitted_bracken",
    "data/processed/DoubleFilter/IBD3_I4_NI4/splitted_bracken",
    "data/processed/DoubleFilter/IBD4_I5_NI5/splitted_bracken",
    "data/processed/DoubleFilter/BS2_NI8/splitted_bracken",
    "data/processed/DoubleFilter/IBD5_I6_NI6/splitted_bracken",
    "data/processed/DoubleFilter/IBD6_I7_NI7/splitted_bracken",
    "data/processed/DoubleFilter/IBD7_I9_NI9/splitted_bracken"
]

for directory in directories:
    # Get all Bracken output files in the directory
    bracken_files = [f for f in os.listdir(directory) if f.endswith('.bracken')]
    
    # Create an empty DataFrame to store the merged data
    merged_df = pd.DataFrame()
    
    for file in bracken_files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path, sep='\t')
        df = df[df['name'] != 'Homo sapiens']
        df = df[['name', 'new_est_reads']]
        
        # Remove .braken suffix from file name and use it as column name
        column_name = file.replace('.bracken', '')
        df.rename(columns={'new_est_reads': column_name}, inplace=True)
        
        # Merge data file by file
        if merged_df.empty:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on='name', how='outer')
    
    # Replace NaN values with 0
    merged_df.fillna(0, inplace=True)
    
    # Create directory to save the merged data
    base_directory = os.path.dirname(directory)
    output_directory = os.path.join(base_directory, "bracken_merged")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Set output file name using the name of the given directory
    dir_name = os.path.basename(os.path.dirname(directory))
    output_file_name = f"{dir_name}_bacterial_count.csv"
    output_file = os.path.join(output_directory, output_file_name)
    merged_df.to_csv(output_file, index=False)

print("All Bracken output files have been merged and saved successfully.")
