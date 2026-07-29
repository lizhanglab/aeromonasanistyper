# AeromonasGStyper
*Aeromonas* Genomic Species Typer. A python script for assignment of genomic species to the *Aeromonas* genus using skANI or fastANI. The tools should assign the same genomic species for a given genome.

## Installation

```
# fastANI or skANI must be installed separately for the program to work!!
git clone https://github.com/lizhanglab/aeromonasgstyper.git
cd aeromonasgstyper
# Recommended pip install in a virtual environment (venv, conda)
pip install .
```

**Note: One of the following dependencies must be installed.**
* [skANI](https://github.com/bluenote-1577/skani)
* [fastANI](https://github.com/ParBLiSS/FastANI)

## Usage

`aeromonasgstyper [-h] -a [skani|fastani] -i QUERYFOLDER -o OUTPUTFILE [-t THREADS]`

`-h`, `--help` show this help message and exit

`-a`, `--ani_tool` choose to run skANI or fastANI

`-i`, `--query` folder containing all input genomes

`-o`, `--output` tabular output file classifications for each genome in query folder

`-t`, `--thread` number of threads to run fastANI with (default: 4)

## Outputs
A tab delimited file with the following columns:

**Note: When the similarity between genomes is too low, fastANI and skANI do not always produce an output (e.g. genome from a different genus).**

1. **Query Genome** : genome name extracted from file name.
2. **Highest ANI Value** : The highest ANI value of the query when compared to all medoid genomes.
3. **Matching medoid genome** : The accession of the highest matching medoid genome.
4. **ANI cluster of the matching medoid genome** : The cluster number of the highest matching medoid genome.
5. ***Aeromonas* genomic species** : The species name assigned to the matching genome at a 95.4% skANI threshold or a 95.6% fastANI threshold. Where the assigned genomic species corresponds to a recognised taxonomic species, the recognised species name is reported. Where the assigned genomic species corresponds to an additional genomic species established in this study that does not correspond to a recognised taxonomic species, the corresponding genomic species designation is reported. Query genomes that do not meet the assignment threshold for any representative medoid genome are reported as a potentially novel genomic species with the information of the closest genomic species. 
