import argparse
import csv
import os
import io
from importlib import resources
from pathlib import Path
import subprocess
import tempfile

def find_files_by_pathlib(directory_path):
    p = Path(directory_path) 
    
    file_extensions = ["fa", "fasta", "fas", "fna"]
    all_files = [
        str(file_path)
        for ext in file_extensions
        for file_path in p.glob(f'*.{ext}')
    ]
    
    return all_files

def get_resource_directory_path():
    return resources.files('aeromonasgstyper.Resources')

def run_fastANI(args):
    temp_directory = "fastANI_result"
    if not os.path.exists(temp_directory):
        os.mkdir(temp_directory)

    # Determine the path for reference genomes
    if args.reference and os.path.isdir(args.reference):
        # User provided existing directory path
        print(f"Using user-provided reference genome folder: {args.reference}")
        reference_genomes = find_files_by_pathlib(args.reference)
    else:
        # Use installed resources
        print("Using bundled reference genome folder.")
        with resources.as_file(resources.files('aeromonasgstyper.Resources')) as installed_resource_path:
            reference_genomes = find_files_by_pathlib(installed_resource_path)

    query_genomes = find_files_by_pathlib(args.query)

    # Create temporary files and run fastANI
    with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=temp_directory) as ql_file, \
             tempfile.NamedTemporaryFile(mode='w', delete=False, dir=temp_directory) as rl_file:
        
        ql_file.close()
        rl_file.close()

            raw_ANI_result = os.path.join(temp_directory, 'fastani_output.txt')
            fastani_command = ['fastANI', "-t", str(args.thread),'--ql', ql_file.name, '--rl', rl_file.name, '-o', raw_ANI_result]
            
            try:
                subprocess.run(fastani_command, check=True)
                print("FastANI run completed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"FastANI run encountered an error: {e}")
            finally:
                if os.path.exists(ql_file.name):
                    os.remove(ql_file.name)
                if os.path.exists(rl_file.name):
                    os.remove(rl_file.name)

    return raw_ANI_result

def ksi(fastANI_output, args):
    genomic_species = {}
    # Determine the source for the reference list
    if args.reference_list and os.path.exists(args.reference_list):
        # User provided existing file path
        print(f"Using user-provided reference list file: {args.reference_list}")
        with open(args.reference_list, mode='r', newline='', encoding='utf-8') as tsvfile:
            tsv_reader = tsvfile.read()
    else:
        # Use installed resources
        print("Using bundled reference list file.")
        try:
            tsv_reader = resources.read_text('aeromonasgstyper.Resources', 'reference_list.tsv')
        except FileNotFoundError:
            print("CRITICAL ERROR: Could not find bundled 'reference_list.tsv'. Installation may be corrupted.")
            return
        
    # Load Data
    tsv_file = io.StringIO(tsv_content)
    reader = csv.DictReader(tsv_file, delimiter='\t')
    for row in reader:
        genomic_species[row["genome"]] = row["species"]

    highest_ani_values = {}
    with open(fastANI_output, "r") as input_file:
        for line in input_file:
            columns = line.strip().split("\t")
            query_genome = os.path.splitext(os.path.basename(columns[0]))[0]
            reference_genome = os.path.splitext(os.path.basename(columns[1]))[0]
            ani_value = float(columns[2])
            
            if query_genome in highest_ani_values:
                if ani_value > highest_ani_values[query_genome][0]:
                    highest_ani_values[query_genome] = (ani_value, reference_genome)
            else:
                highest_ani_values[query_genome] = (ani_value, reference_genome)
                
    with open(args.output, "w") as output_file:
        output_file.write("Query Genome\tHighest ANI similarity\tReference Genome with the highest ANI similarity\tReference Genomic Species\n")
        
        for query_genome, (highest_ani, reference_genome) in highest_ani_values.items():
            reference_species = genomic_species.get(reference_genome, "UNKNOWN_REFERENCE")
            
            if highest_ani >= 94.2:
                output_file.write(f"{query_genome}\t{highest_ani}\t{reference_genome}\t{reference_species}\n")
            else:
                output_file.write(
                    f"{query_genome}\t{highest_ani}\t{reference_genome}\tNovel (closest {reference_species})\tNovel Aeromonas genomic species\n")

        print(f"Output has been written to {args.output}")


def parseargs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--query", help="input query genome folder. File types .fasta .fas .fa .fna are recognised",
                        required=True)
    parser.add_argument("-r", "--reference", help="folder for reference genomes") 
    
    parser.add_argument("-l", "--reference_list", help="file listing species for reference genomes")
    
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