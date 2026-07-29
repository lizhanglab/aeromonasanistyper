# AeromonasGStyper
*Aeromonas* Genomic Species Typer. A python script for accurate assignment using of species to the *Aeromonas* genus using skANI or fastANI.

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
2. **Highest ANI Value** : The highest ANI value of the query when compared to all centroid genomes.
3. **Matching centroid genome** : The accession of the highest matching centroid genome.
4. **ANI cluster of the matching centroid genome** : The cluster number of the highest matching centroid genome.
5. 
    * ***Aeromonas* genomic species** : The species name assigned to the matching genome at a 95.4% skANI threshold or a 95.6% fastANI threshold. Named species match existing taxonomic species. Genomic species are supported by core genome phylogeny but have not been assigned taxonomic species names formally.
    * **Possible novel genomic species** : When the genome does not match any centroid genome at a 95.4% skANI threshold or a 95.6% fastANI threshold. If no centroid genomes match it indicates that the genome could represent a new genomic species. The highest match is still included but it is not reliable.
