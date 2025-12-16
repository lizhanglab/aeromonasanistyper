import argparse
import csv
import os
from pathlib import Path
import subprocess
import tempfile

#example run: python aeromonasgstyper.py --query folder_path --output ./testing_output.txt --thread 4

def find_files_by_pathlib(directory_path):
    p = Path(directory_path) 
    
    # Use a list comprehension to iterate over extensions and glob for each
    file_extensions = ["fa", "fasta", "fas", "fna"]
    all_files = [
        str(file_path) # Convert Path object back to string for consistency
        for ext in file_extensions
        for file_path in p.glob(f'*.{ext}')
    ]
    
    return all_files

def run_fastANI(args):
    temp_directory = "fastANI_result"
    if not os.path.exists(temp_directory):
        os.mkdir(temp_directory)
    # Create two temporary files in the fastani result folder
    with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=temp_directory) as ql_file, \
            tempfile.NamedTemporaryFile(mode='w', delete=False, dir=temp_directory) as rl_file:
        query_genomes = find_files_by_pathlib(args.query)
        reference_genomes = find_files_by_pathlib(args.reference)
        for file in query_genomes:
            ql_file.write(file + '\n')
            print(file)
        for file in reference_genomes:
            rl_file.write(file + '\n')
    print(ql_file)
    raw_ANI_result= os.path.join(temp_directory, 'fastani_output.txt')
    fastani_command = ['fastANI', "-t", str(args.thread),'--ql', ql_file.name, '--rl', rl_file.name, '-o', raw_ANI_result]
    try:
        subprocess.run(fastani_command, check=True)
        print("FastANI run completed successfully.")
        # Remove the temporary files after FastANI run
        os.remove(ql_file.name)
        os.remove(rl_file.name)
    except subprocess.CalledProcessError:
        print("FastANI run encountered an error.")

    return raw_ANI_result

def ksi(fastANI_output, args):
    # Load dictionary for reference genome to species
    genomic_species = {}
    with open(args.reference_list, mode='r', newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            genomic_species[row["genome"]] = row["species"]

    highest_ani_values = {}
    with open(fastANI_output, "r") as input_file:
        for line in input_file:
            columns = line.strip().split("\t")
            # Extract the query genome, reference genome, and ANI value.
            query_genome = os.path.splitext(os.path.basename(columns[0]))[0]
            reference_genome = os.path.splitext(os.path.basename(columns[1]))[0]
            ani_value = float(columns[2])
            # Check if the query genome is already in the dictionary.
            if query_genome in highest_ani_values:
                # If yes, compare the ANI value with the existing highest value.
                if ani_value > highest_ani_values[query_genome][0]:
                    highest_ani_values[query_genome] = (ani_value, reference_genome)
            else:
                # If no, add the query genome to the dictionary.
                highest_ani_values[query_genome] = (ani_value, reference_genome)
    # Open and write to the output text file.
    with open(args.output, "w") as output_file:
        output_file.write("Query Genome\tHighest ANI similarity\tReference Genome with the highest ANI similarity\tReference Genomic Species\n")
        # Write the data to the output file.
        for query_genome, (highest_ani, reference_genome) in highest_ani_values.items():
            if highest_ani >= 94.2:
                # If yes, output the ANI genomic species and the genomic species
                output_file.write(f"{query_genome}\t{highest_ani}\t{reference_genome}\t{genomic_species[reference_genome]}\n")
            else:
                # If not, indicate this is a isolate belong to a novel genomic species
                output_file.write(
                    f"{query_genome}\t{highest_ani}\t{reference_genome}\tNovel (closest {genomic_species[reference_genome]})\tNovel Aeromonas genomic species\n")

        print(f"Output has been written to {args.output}")

def parseargs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--query", help="input query genome folder. File types .fasta .fas .fa .fna are recognised",
                        required=True)
    parser.add_argument("-r", "--reference", help="folder for reference genomes",
                        default="reference_genomes")
    parser.add_argument("-l", "--reference_list", help="file listing species for reference genomes",
                        default="reference_list.tsv")
    parser.add_argument("-o", "--output", help="species identifier output tsv file", 
                        required=True)
    parser.add_argument("-t", "--thread", help="number of threads to run fastANI",
                        default=4)
    args = parser.parse_args()
    return args
def main():
    args = parseargs()
    fastANI_output = run_fastANI(args)
    ksi(fastANI_output, args)

if __name__ == '__main__':
    main()