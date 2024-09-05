import os
import subprocess

# Define the base paths for data processing and the Kraken database
base_path = 'data/processed/DoubleFilter/'
kraken_db_path = '/home/jsy/2022_pathogentrack/db_big_kraken/'

# Function to run kraken2 and bracken for each cell barcode
def run_kraken_bracken(barcode):
    R1_file = os.path.join(input_path, f'{barcode}_R1.fastq')
    R2_file = os.path.join(input_path, f'{barcode}_R2.fastq')
    kraken_report_file = os.path.join(kraken_path, f'{barcode}.k2report')
    kraken_output_file = os.path.join(kraken_path, f'{barcode}.kraken2')
    bracken_output_file = os.path.join(bracken_path, f'{barcode}.bracken')

    # Execute Kraken2 for taxonomic classification
    kraken2_command = f"kraken2 --db {kraken_db_path} --threads 2048 --report {kraken_report_file} --report-minimizer-data --minimum-hit-groups 3 {R1_file} {R2_file} > {kraken_output_file}"
    subprocess.run(kraken2_command, shell=True)

    # Execute Bracken for abundance estimation
    bracken_command = f"bracken -d {kraken_db_path} -i {kraken_report_file} -o {bracken_output_file} -r 100 -l S -t 1"
    subprocess.run(bracken_command, shell=True)

# Function to process a specific dataset
def process_dataset(dataset):
    # Define the paths
    global input_path
    input_path = os.path.join(base_path, dataset, 'splitted_fastq/')
    global kraken_path
    kraken_path = os.path.join(base_path, dataset, 'splitted_kraken/')
    global bracken_path
    bracken_path = os.path.join(base_path, dataset, 'splitted_bracken/')
    
    # Create directories if not exists
    os.makedirs(kraken_path, exist_ok=True)
    os.makedirs(bracken_path, exist_ok=True)
    
    # Get the list of files in the input directory
    file_list = [f for f in os.listdir(input_path) if f.endswith('.fastq')]
    
    # Group files by cell barcode
    file_dict = {}
    for file in file_list:
        barcode = file.split('_R')[0]
        if barcode not in file_dict:
            file_dict[barcode] = [file]
        else:
            file_dict[barcode].append(file)
    # Function to identify missing barcodes
    def get_missing_barcodes():
        bracken_files = os.listdir(bracken_path)
        bracken_barcodes = set([os.path.splitext(file)[0].rsplit('.', 1)[0] for file in bracken_files])
        return set(file_dict.keys()) - bracken_barcodes

    # Initial processing of all barcodes
    print(f"Starting initial processing for dataset {dataset}...")
    for barcode, _ in file_dict.items():
        run_kraken_bracken(barcode)

    # Process missing barcodes
    max_attempts = 5
    attempt = 1
    missing_barcodes = get_missing_barcodes()

    while len(missing_barcodes) > 0 and attempt <= max_attempts:
        print(f"Attempt {attempt}: Processing {len(missing_barcodes)} missing barcodes...")
        for barcode in missing_barcodes:
            run_kraken_bracken(barcode)
        missing_barcodes = get_missing_barcodes()
        attempt += 1

    if len(missing_barcodes) > 0:
        print(f"Failed to process {len(missing_barcodes)} barcodes after {max_attempts} attempts.")
        print(f"Failed cell barcodes: {missing_barcodes}")
    else:
        print(f"All barcodes processed successfully after {attempt-1} attempt(s).")

    print(f"Total barcodes processed: {len(file_dict) - len(missing_barcodes)}")

# Call the function with the dataset to process
datasets = ['IBD7_I9_NI9']
for dataset in datasets:
    process_dataset(dataset)
