import os
import glob
import subprocess

# Define an array of sample directories
samples = ["IBD7_I9_NI9"]

# Iterate through each sample
for sample in samples:
    # Define file paths for paired-end reads of spatial transcriptomics data across sequencing lanes
    file1 = glob.glob(f"data/raw/SpatialTranscriptomicsData/{sample}/Fastq/*L001_R1_001.fastq.gz")[0]
    file2 = glob.glob(f"data/raw/SpatialTranscriptomicsData/{sample}/Fastq/*L002_R1_001.fastq.gz")[0]
    file3 = glob.glob(f"data/raw/SpatialTranscriptomicsData/{sample}/Fastq/*L001_R2_001.fastq.gz")[0]
    file4 = glob.glob(f"data/raw/SpatialTranscriptomicsData/{sample}/Fastq/*L002_R2_001.fastq.gz")[0]

    # Create the output directory
    output_dir = f"data/processed/SingleFilter/{sample}/nonhuman_read"
    os.makedirs(output_dir, exist_ok=True)

    # Execute Bowtie2 for human read removal
    # Unaligned (non-human) reads are retained in the output file
    bowtie2_command = [
        "bowtie2",
        "-x", "/home/jsy/2023_bowtie2/GRCh38",
        "-p", "48",
        "-q",
        "-1", f"{file1},{file2}",
        "-2", f"{file3},{file4}",
        "--un-conc", f"{output_dir}/nonhuman_reads.fa"
    ]

    # Run the Bowtie2 command
    subprocess.run(bowtie2_command)
