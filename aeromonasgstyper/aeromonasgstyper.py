import sys
import argparse
if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources
import csv
import os
from pathlib import Path
import subprocess
import tempfile
import shutil

def find_files_by_pathlib(directory_path):
    p = Path(directory_path)
    file_extensions = ["fa", "fasta", "fas", "fna"]
    return [
        str(file_path)
        for ext in file_extensions
        for file_path in p.glob(f'*.{ext}')
    ]


def get_resource_directory_path():
    return resources.files('aeromonasgstyper.Resources')


def get_genome_directory_path():
    return resources.files('aeromonasgstyper.Resources') / 'genomes'


def _resolve_reference_genomes(args):
    if args.reference and os.path.isdir(args.reference):
        print(f"Using user-provided reference genome folder: {args.reference}")
        return find_files_by_pathlib(args.reference), None
    else:
        print("Using bundled reference genome folder.")
        bundled_path = get_genome_directory_path()
        return find_files_by_pathlib(bundled_path), None


def _write_genome_list(paths, file_obj):
    for p in paths:
        file_obj.write(p + '\n')


# fastANI

def run_fastani(args, out_dir, temp_dir):
    """Run fastANI and return path to raw output file."""
    reference_genomes, _ = _resolve_reference_genomes(args)
    query_genomes = find_files_by_pathlib(args.query)

    if not query_genomes:
        print(f"Error: No valid fasta files found in query path: {args.query}")
        return None

    with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=temp_dir) as ql, \
         tempfile.NamedTemporaryFile(mode='w', delete=False, dir=temp_dir) as rl:

        _write_genome_list(query_genomes, ql)
        _write_genome_list(reference_genomes, rl)
        ql.close(); rl.close()

        raw_output = os.path.join(out_dir, 'fastani_output.txt')
        cmd = ['fastANI', '-t', str(args.thread),
               '--ql', ql.name, '--rl', rl.name, '-o', raw_output]

        try:
            subprocess.run(cmd, check=True)
            print("fastANI run completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"fastANI run encountered an error: {e}")
            return None
        finally:
            for f in (ql.name, rl.name):
                if os.path.exists(f):
                    os.remove(f)

    return raw_output


# skANI

def _get_reference_sketch_dir(args):
    if args.reference and os.path.isdir(args.reference):
        return Path(args.reference) / "sketches"
    else:
        return get_resource_directory_path() / "sketches"


def _ensure_reference_sketches(args, reference_genomes):
    sketch_dir = _get_reference_sketch_dir(args)
    existing = list(sketch_dir.glob("*.sketch")) if sketch_dir.exists() else []

    if sketch_dir.exists() and len(existing) == len(reference_genomes):
        print(f"Using cached reference sketches from: {sketch_dir}")
        return str(sketch_dir)

    if sketch_dir.exists() and existing:
        print(f"Reference panel size changed ({len(existing)} sketches vs "
              f"{len(reference_genomes)} genomes) — rebuilding sketches.")
    else:
        print(f"Building reference sketches for the first time in: {sketch_dir}")

    if sketch_dir.exists():
        shutil.rmtree(sketch_dir)
    sketch_dir.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as rl:
        _write_genome_list(reference_genomes, rl)
        rl.close()
        cmd = ['skani', 'sketch',
               '-l', rl.name,
               '-o', str(sketch_dir),
               '-t', str(args.thread)]
        try:
            subprocess.run(cmd, check=True)
            print("Reference sketch build completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"skANI sketch encountered an error: {e}")
            return None
        finally:
            if os.path.exists(rl.name):
                os.remove(rl.name)

    return str(sketch_dir)


def run_skani(args, out_dir, temp_dir):
    """Run skANI search and return normalised output path."""
    reference_genomes, _ = _resolve_reference_genomes(args)
    query_genomes = find_files_by_pathlib(args.query)
    sketch_dir = _ensure_reference_sketches(args, reference_genomes)

    if sketch_dir is None:
        print("Failed to build reference sketches. Exiting.")
        return None

    if not query_genomes:
        print(f"Error: No valid fasta files found in query path: {args.query}")
        return None

    raw_output  = os.path.join(out_dir, 'skani_output.txt')

    with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=temp_dir) as ql:
        _write_genome_list(query_genomes, ql)
        ql.close()

        # skani search queries a sketch database (-d)
        cmd = ['skani', 'search',
               '-t', str(args.thread),
               '--ql', ql.name,
               '-d',  sketch_dir,
               '-o',  raw_output]

        try:
            subprocess.run(cmd, check=True)
            print("skANI search completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"skANI search encountered an error: {e}")
            return None
        finally:
            if os.path.exists(ql.name):
                os.remove(ql.name)

    # Normalise column order: skani outputs Ref, Query, ANI — reorder to Query, Ref, ANI
    with open(raw_output) as fin, open(norm_output, 'w') as fout:
        for i, line in enumerate(fin):
            if i == 0 and line.startswith("Ref_file"):
                continue  # skip header
            cols = line.strip().split('\t')
            if len(cols) < 3:
                continue
            ref_file, query_file, ani = cols[0], cols[1], cols[2]
            fout.write(f"{query_file}\t{ref_file}\t{ani}\n")

    return norm_output


# Species ID

def _load_reference_species(args):
    if args.reference_list and os.path.exists(args.reference_list):
        print(f"Using user-provided reference list file: {args.reference_list}")
        with open(args.reference_list, encoding='utf-8') as f:
            tsv_content = f.read()
    else:
        print("Using bundled reference list file.")
        tsv_path = get_resource_directory_path() / 'reference_list.tsv'
        if not tsv_path.exists():
            print(f"CRITICAL ERROR: Could not find bundled 'reference_list.tsv' at {tsv_path}.")
            sys.exit(1)
        with open(tsv_path, encoding='utf-8') as f:
            tsv_content = f.read()

    species_map = {}
    reader = csv.DictReader(tsv_content.splitlines(), delimiter='\t')
    for row in reader:
        species_map[row["genome"]] = row["species"]
    return species_map


def ksi(ani_output, args, threshold, final_tsv_path):
    species_map = _load_reference_species(args)

    highest_ani_values = {}
    with open(ani_output) as f:
        for line in f:
            cols = line.strip().split('\t')
            if len(cols) < 3:
                continue
            query_stem = os.path.splitext(os.path.basename(cols[0]))[0]
            ref_stem   = os.path.splitext(os.path.basename(cols[1]))[0]
            try:
                ani_value = float(cols[2])
            except ValueError:
                continue

            if query_stem not in highest_ani_values or \
               ani_value > highest_ani_values[query_stem][0]:
                highest_ani_values[query_stem] = (ani_value, ref_stem)

    with open(final_tsv_path, 'w') as out:
        tool_name = args.ani_tool.lower()
        out.write(
            f"Query Genome\t"
            f"Highest ANI similarity ({tool_name}, threshold: {threshold}%)\t"
            f"Reference Genome with the highest ANI similarity\t"
            f"Reference ANI Species\n"
        )

        for query, (highest_ani, ref_genome) in highest_ani_values.items():
            ref_species = species_map.get(ref_genome, "UNKNOWN_REFERENCE")

            if round(highest_ani, 1) >= threshold:
                out.write(f"{query}\t{highest_ani}\t{ref_genome}\t{ref_species}\n")
            else:
                out.write(
                    f"{query}\t{highest_ani}\t{ref_genome}\t"
                    f"Novel (closest {ref_species})\t"
                    f"Potential Novel Aeromonas ANI species\n"
                )

    print(f"Final species identification saved to: {final_tsv_path}")


# CLI

def parseargs():
    parser = argparse.ArgumentParser(
        description='A tool for Aeromonas species identification using ANI.',
        usage='aeromonasgstyper -a <fastani|skani> -i <query_folder> -o <output_directory> [OPTIONS]'
    )

    required = parser.add_argument_group('Required Inputs')
    required.add_argument(
        "-a", "--ani_tool",
        choices=["fastani", "skani"],
        required=True,
        help="ANI tool to use: 'fastani' or 'skani'"
    )
    required.add_argument(
        "-i", "--query",
        required=True,
        help="Input query genome folder (.fasta .fas .fa .fna recognised)"
    )
    required.add_argument(
        "-o", "--output",
        required=True,
        help="Output directory where all result files and intermediate outputs will be saved"
    )

    ref = parser.add_argument_group('Reference Input Options')
    ref.add_argument("-r", "--reference",      help="Folder for reference genomes")
    ref.add_argument("-l", "--reference_list", help="TSV file listing species for reference genomes")

    thresh = parser.add_argument_group('ANI Threshold Options')
    thresh.add_argument("--fastani_threshold", type=float, default=95.4, metavar="FLOAT", help="ANI threshold for fastANI species assignment (default: 95.4)")
    thresh.add_argument("--skani_threshold", type=float, default=95.2, metavar="FLOAT", help="ANI threshold for skANI species assignment (default: 95.2)")

    threads = parser.add_argument_group('Thread Settings')
    threads.add_argument("-t", "--thread", type=int, default=4, help="Number of threads (default: 4)")

    return parser.parse_args()


def main():
    args = parseargs()

    # 1. Ensure the primary output directory exists
    out_dir = os.path.abspath(args.output)
    os.makedirs(out_dir, exist_ok=True)

    # 2. Setup internal temp directory within output folder
    temp_dir = os.path.join(out_dir, ".tmp_ani")
    os.makedirs(temp_dir, exist_ok=True)
    
    final_tsv_path = os.path.join(out_dir, "species_identification.tsv")

    try:
        if args.ani_tool == "fastani":
            threshold  = args.fastani_threshold
            ani_output = run_fastani(args, out_dir, temp_dir)
            final_tsv_path = os.path.join(out_dir, "species_identification_fastani.tsv")
        elif args.ani_tool == "skani":
            threshold  = args.skani_threshold
            ani_output = run_skani(args, out_dir, temp_dir)
            final_tsv_path = os.path.join(out_dir, "species_identification_skani.tsv")

        if ani_output and os.path.exists(ani_output):
            ksi(ani_output, args, threshold, final_tsv_path)
        else:
            print("ANI run did not produce valid output. Exiting.")
            sys.exit(1)

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    main()