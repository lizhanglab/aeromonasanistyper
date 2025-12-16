# AeromonasGStyper
Aeromonas Genomic Species Typer. A python script for accurate assignment of ANI genomic species to the Aeromonas genus.

## Installation

```
git clone https://github.com/lizhanglab/aeromonasgstyper.git
cd aeromonasgstyper
python setup.py install
```

**Note: the following dependencies must be installed**
* [fastANI](https://github.com/ParBLiSS/FastANI)

## Usage

`aeromonasgstyper [-h] -i QUERYFOLDER -o OUTPUTFILE [-t THREADS]`

`-h`, `--help` show this help message and exit

`-i`, `--query` folder containing all input genomes

`-o`, `--output` tabular output file classifications for each genome in query folder

`-t`, `--thread` number of threads to run fastANI with (default: 4)

## Outputs
A tab delimited file with the following columns:
* **Query Genome** : genome name extracted from file name
* **Highest ANI Value** : The highest ANI value of the query when compared to all centroid genomes
* **Matching centroid genome** : The accession of the highest matching centroid genome
* **Aeromonas Genomic Species** : The genomic species name assigned to the matching ANI cluster
* **Possible Novel genomic species** : When this genome does not match any centroid genome at 95.6% ANI. If no centroid genomes match it indicates that the genome could represent a new species. If true, the highest match is still included but it is not reliable.