import os
import glob
import subprocess

# Define the array of directories
samples = ["IBD7_I9_NI9"]

# Iterate through each sample
for sample in samples:
    # Define file paths for paired-end reads of spatial transcriptomics data across sequencing lanes
    file1 = glob.glob(f"data/raw/SpatialTranscriptomicsData/{sample}/Fastq/*L001_R1_001.fastq.gz")[0]
    file2 = glob.glob(f"data/raw/SpatialTranscriptomicsData/{sample}/Fastq/*L002_R1_001.fastq.gz")[0]
    file3 = glob.glob(f"data/raw/SpatialTranscriptomicsData/{sample}/Fastq/*L001_R2_001.fastq.gz")[0]
    file4 = glob.glob(f"data/raw/SpatialTranscriptomicsData/{sample}/Fastq/*L002_R2_001.fastq.gz")[0]

    # Create the output directories if they don't exist
    os.makedirs(f"data/processed/DoubleFilter/{sample}/bwa_SAM", exist_ok=True)
    os.makedirs(f"data/processed/DoubleFilter/{sample}/bowtie_nonhuman_fa", exist_ok=True)

    # Run the BWA MEM command for human read removal (1st removal step)
    bwa_command_L001 = [
        "bwa", "mem", "/home/jsy/2023_bowtie2/GCA_000001405.28_GRCh38.p13_genomic.fna",
        file1, file3
    ]
    bwa_command_L002 = [
        "bwa", "mem", "/home/jsy/2023_bowtie2/GCA_000001405.28_GRCh38.p13_genomic.fna",
        file2, file4
    ]
    with open(f"data/processed/DoubleFilter/{sample}/bwa_SAM/output_L001.sam", "w") as outfile:
        subprocess.run(bwa_command_L001, stdout=outfile)
    with open(f"data/processed/DoubleFilter/{sample}/bwa_SAM/output_L002.sam", "w") as outfile:
        subprocess.run(bwa_command_L002, stdout=outfile)

    # Extract unmapped reads from L001 and L002 SAM files
    samtools_view_L001 = [
        "samtools", "view", "-b", "-f", "4",
        f"data/processed/DoubleFilter/{sample}/bwa_SAM/output_L001.sam"
    ]
    samtools_view_L002 = [
        "samtools", "view", "-b", "-f", "4",
        f"data/processed/DoubleFilter/{sample}/bwa_SAM/output_L002.sam"
    ]
    samtools_fastq_L001 = [
        "samtools", "fastq",
        f"data/processed/DoubleFilter/{sample}/bwa_SAM/unmapped_L001.bam"
    ]
    samtools_fastq_L002 = [
        "samtools", "fastq",
        f"data/processed/DoubleFilter/{sample}/bwa_SAM/unmapped_L002.bam"
    ]

    # Run samtools commands to convert SAM to BAM and FASTQ
    with open(f"data/processed/DoubleFilter/{sample}/bwa_SAM/unmapped_L001.bam", "wb") as bamfile:
        subprocess.run(samtools_view_L001, stdout=bamfile)
    with open(f"data/processed/DoubleFilter/{sample}/bwa_SAM/unmapped_L001.fastq", "w") as fastqfile:
        subprocess.run(samtools_fastq_L001, stdout=fastqfile)
    with open(f"data/processed/DoubleFilter/{sample}/bwa_SAM/unmapped_L002.bam", "wb") as bamfile:
        subprocess.run(samtools_view_L002, stdout=bamfile)
    with open(f"data/processed/DoubleFilter/{sample}/bwa_SAM/unmapped_L002.fastq", "w") as fastqfile:
        subprocess.run(samtools_fastq_L002, stdout=fastqfile)

    # Run Bowtie2 on the processed FASTQ files for human read removal (2nd removal step)
    bowtie2_command = [
        "bowtie2", "--very-sensitive", "-k", "16", "--np", "1", "--mp", "1,1",
        "--rdg", "0,1", "--rfg", "0,1", "--score-min", "L,0,-0.05",
        "-x", "/home/jsy/2023_bowtie2/CHM13/chm13.draft_v1.0_plusY", "-p", "48", "-q",
        "-1", f"data/processed/DoubleFilter/{sample}/bwa_SAM/unmapped_L001.fastq",
        "-2", f"data/processed/DoubleFilter/{sample}/bwa_SAM/unmapped_L002.fastq",
        "--un-conc", f"data/processed/DoubleFilter/{sample}/bowtie_nonhuman_fa/nonhuman_reads.fa"
    ]
    
    # Run Bowtie2 command
    subprocess.run(bowtie2_command)
