# Data specification

This specification captures the data files and semantic hierarchy for representing genomics 
data as a collection of chromosomes with point and peak arrays applied along a 3D structure.

**Assumptions:**
- The top level collection of data is a `project`
- A project is a series of `experiments` 
    - an `experiment` is a collection of results with a semantic meaning.
- All data within a project has the same chromosomes, experiments, timesteps and arrays.
- The chromosome structure will be represented in 3D space as a smooth curve constrained 
  by the points in the structure file.
- Each chromosome's position in 3D space is in global coordinates. If two chromosomes are 
  loaded into the same dataset/view, they would be represented correctly relative to each other.
- The `.narrowPeak` and `.bed` files will contain data for all chromosomes in the genome, but
  the `structure.csv` will not necessarily contain all of those chromosomes. If there is
  not an entry for a chromosome in the `structure.csv` file, the data cannot be visualized.
- The chromosome name in all files is not a *common name* (such as 'chromosome 21'),
  but it can be mapped to a common name with the information in the `chromosomes.yaml` file.
  The chromosome name is consistent across all files in a project.

## genome

A genome is the genetic information for an organism. It is a sequence of nucleotides of
(in our case) DNA, made up of base pairs of adenine, cytosine, guanine and thymine.

A genome is typically represented by a linear sequence of base pairs. Each base pair has
a unique ID that is its position along the linear sequence.

The IDs of a genome is a 1-based sequence of numbers.

## chromosome

A chromosome is a linear sequence of `n` base pairs in a genome. it is uniquely identified
by a begin and end ID along the genome sequence.

A `project` need not contain all possible chromosomes for a genome. However, all structure
and track files will contain the same set of chromosomes.

In general the name of a chromosome in these files will be a *terrible name* string that 
is not readily associated with the common name (chromosome 12, etc.) of a chromosome. The 
mapping of the *terrible name* to a common name can be found in the `chromosomes.yaml` file
at the top of the project hierarchy.


## ID

In all contexts, an `ID` is a one-based integer that is the position of a base pair along
the genome. A chromosome has a [begin, end] pair that identifies its place along the
genome. A variable has `ID` values that also reference the genome. 

## project data hierarchy 

Semantically makes the *experiment* the top of the hierarchy.

```
project/
    genes.csv                           important genes within the genome 
    chromosomes.yaml                    information about chromosomes
    species.gff                         genomic information about the species
    experiment_001/
        meta.yaml                       experiment metadata
        001/                            timestep
            meta.yaml                   timestep metadata
            structure.csv               structure
            trackname_001.narrowPeak    peak variable file (one or more of these)
            ...
            compartment.bed             compartment variable file (only one of these)
        ...
    experiment_002/
    ...
    experiment_nnn/
```

## structure file specification

This file contains structure data for the genome a single timestep of the experiment.
The data is organized by chromosomes (first column). It need not contain information for
all chromosomes that appear in the `.gff` file. It will always have a value for the start
and end ids of the chromosome, regardless of the resolution of the structure data. 
The *resolution* of the chromosomes need not be the same.

```
chromosome,id,x,y,z
<string>,<int>,<float>,<float>,<float>
```


## `.narrowPeak` file specification

This file contains peak variable information for a single timestep for a single variable.
The name of the file is the name of the variable.

This is the semantic meaning of the columns in this file. The value for the `start_id` and
`end_id` is zero, and the value at `mid_id` is `midpont_value` (note that the value in this
column is 1/10.0 the midpoint_value):

```
chromosome_name start_id end_id unused unused unused unused unused midpoint_value/10.0 midpoint_id
```

These are the data type of the columns in this file:

```
<string> <int> <int> <string> <int> <string> <float> <float> <float> <float> <int>
```

This is an example of data in a `narrowPeak` file:

```
NC_023642.1   421    675 2803_001_autosomes_peak_1   29 . 3.84937 4.75735 2.97448 187
NC_023642.1   939   1051 2803_001_autosomes_peak_2   14 . 2.88702 3.05827 1.41458 49
NC_023642.1  2156   2539 2803_001_autosomes_peak_3   88 . 6.73639 10.9183 8.89845 227
NC_023642.1  2700   3297 2803_001_autosomes_peak_4a  67 . 5.77405 8.71856 6.76339 83
NC_023642.1  2700   3297 2803_001_autosomes_peak_4b 185 . 10.5858 20.7783 18.5562 257
NC_023642.1  5376   6284 2803_001_autosomes_peak_5   67 . 5.77405 8.71856 6.76339 124
NC_023642.1  6975   7376 2803_001_autosomes_peak_6   38 . 4.33054 5.68452 3.84989 280
NC_023642.1  7674   7798 2803_001_autosomes_peak_7   29 . 3.84937 4.75735 2.97448 47
NC_023642.1  9474   9636 2803_001_autosomes_peak_8   14 . 2.88702 3.05827 1.41458 25
NC_023642.1 16621  19699 2803_001_autosomes_peak_9a 429 . 18.7657 45.4897 42.9587 821
```

## `compartment.bed` file specification

This contains values defined along spans of the chromosome. The entire chromosome need not
have associated values. This is the semantic meaning of the columns in this file:

```
chromosome_name start_id end_id value
```

These are the data types of the columns:

```
<string> <int> <int> <float>
```
