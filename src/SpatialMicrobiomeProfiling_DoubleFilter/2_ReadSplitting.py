import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

sample_name = "IBD7_I9_NI9"

# Define paths for spatial transcriptomis barcode file and output path for processed barcode files
barcode_tsv_path = f"data/raw/SpatialTranscriptomicsData/{sample_name}/Spatial_matrix/barcodes.tsv"
save_barcode_path = f"data/processed/DoubleFilter/{sample_name}/barcode_tsv/"

# Directory for splitted fastq files of non-human reads
splitted_fastq_dir = f"data/processed/DoubleFilter/{sample_name}/splitted_fastq/"

# Create output directory for processed barcode files if they don't exist
if not os.path.exists(save_barcode_path):
    os.makedirs(save_barcode_path)

# Process spatial transcriptomics barcode file
with open(barcode_tsv_path, 'r') as f:
    lines = f.readlines()
    
for line in lines:
    # Remove '-1' suffix and whitespace from barcode
    barcode = line.replace('-1\n', '')

    file_save_barcode_path = os.path.join(save_barcode_path, f'{barcode}.txt')

    # Save processed barcode file
    with open(file_save_barcode_path, 'w') as f:
        f.write(barcode)

# Create output directory for splitted fastq files if they don't exist
if not os.path.exists(splitted_fastq_dir):
    os.makedirs(splitted_fastq_dir)

# Define function to execute UMI tool for splitting non-human reads by cell barcode
def run_cmd_umi(barcode):
    cmd_umi = f"""
    umi_tools extract --bc-pattern=CCCCCCCCCCCCCCCCNNNNNNNNNN \
    --stdin data/processed/DoubleFilter/{sample_name}/nonhuman_read/nonhuman_reads.1.fa \
    --stdout {splitted_fastq_dir}/{barcode}_R1.fastq \
    --read2-in data/processed/DoubleFilter/{sample_name}/nonhuman_read/nonhuman_reads.2.fa \
    --read2-out={splitted_fastq_dir}/{barcode}_R2.fastq \
    --whitelist={save_barcode_path}{barcode}.txt
    """
    subprocess.run(cmd_umi, shell=True)

# Get list of cell barcodes from processed barcode files
barcodes = [os.path.splitext(barcode_file)[0] for barcode_file in os.listdir(save_barcode_path)]

# Use ProcessPoolExecutor for parallel processing of UMI tool
print("Starting initial processing of all cell barcodes...")
with ProcessPoolExecutor(max_workers = 100) as executor:
    executor.map(run_cmd_umi, barcodes)

# Check if all cell barcodes have been processed
fastq_files = os.listdir(splitted_fastq_dir)

# Function to identify missing barcodes
def get_missing_barcodes():
    # Extract barcodes from splitted fastq files
    fastq_barcodes = set([os.path.splitext(file)[0].rsplit('_', 1)[0] for file in fastq_files])
    # Return set of barcodes that have not been processed
    return set(barcodes) - fastq_barcodes

# Process missing barcodes
max_attempts = 5 # Maximal number of attempts to process missing barcodes
attempt = 1
missing_barcodes = get_missing_barcodes()

while len(missing_barcodes) > 0 and attempt <= max_attempts:
    print(f"Attempt {attempt}: Processing {len(missing_barcodes)} missing barcodes...")
    with ProcessPoolExecutor() as executor:
        executor.map(run_cmd_umi, missing_barcodes)
    
    missing_barcodes = get_missing_barcodes()
    attempt += 1

if len(missing_barcodes) > 0:
    print(f"Failed to process {len(missing_barcodes)} barcodes after {max_attempts} attempts.")
    print(f"Failed cell barcodes: {missing_barcodes}")
else:
    print(f"All barcodes processed successfully after {attempt-1} attempt(s).")

print(f"Total barcodes processed: {len(barcodes) - len(missing_barcodes)}")