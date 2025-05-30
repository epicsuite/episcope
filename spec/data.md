# Data specification

This specification captures the data files and semantic hierarchy for representing genomics data as a collection of chromosomes with point and peak arrays applied along a 3D structure.

Assumptions:
- The top level collection of data is a `project`
- A project is a series of `experiments` 
    - an `experiment` is a collection of results with a semantic meaning.
- All data within a project has the same chromosomes, experiments, timesteps and arrays.
- The chromosome structure will be represented in 3D space as a smmooth curve constrained by the points in the structure file.
- Each chromosome's position in 3D space is in global coordinates. If two chromosomes are loaded into the same dataset/view, they would be represented correctly relative to each other.


## genome

A genome is the genetic information for an organism. It is a sequence of nucleotides of
(in our case) DNA, made up of base pairs of adenine, cytosine, guanine and thymine.

A genome is typically represented by a linear sequence of base pairs. Each base pair has
a unique ID that is its position along the linear sequence.

The IDs of a genome is a 1-based sequence of numbers.

## chromosome

A chromosome is a linear sequence of `n` base pairs in a genome. it is uniquely identified
by a begin and end ID along the genome sequence.

## ID

In all contexts, an `ID` is a one-based integer that is the position of a base pair along
the genome. A chromosome has a [begin, end] pair that identifies its place along the
genome. A variable has `ID` values that also reference the genome. 

## chromosome-based hierarchy option

Semantically makes the *chromosome* the top of the hierarchy.

```
project/
    species/
        somefile.gff            genomic information about the species
    chr1/                       chromosome
        meta.json               metadata
        untreated/              experiment
            001/                timestep
                meta.json       timestep metadata
                structure.csv   structure
                point001.csv    point variable file (1 to n of these)
                ...
                peak001.csv     peak variable file  (1 to n of these)
                ...
        infected/
        ...
        exp_001/
    chr2/
    ...
    chrn/
```

## experiment-based hierarchy option 

Semantically makes the *experiment* the top of the hierarchy.

```
project/
    species/
        somefile.gff            genomic information about the species
    experiment_001/
        meta.json               experiment metadata
        chr1/                   chromosome
            meta.json           metadata
            genes.csv           important genes within the chromosome
            001/                timestep
                meta.json       timestep metadata
                structure.csv   structure
                point001.csv    point variable file (1 to n of these)
                ...
                peak001.csv     peak variable file  (1 to n of these)
                ...
        ...
    experiment_002/
    ...
    experiment_nnn/
```

## experiment-based filename

```
    experiment_001/
        chr1_001_point001.csv
        chr1_001_point001.csv
        chr1_001_peak001.csv
        chr1_001_peak001.csv
```


## structure.csv
The `structure.csv` file defines a line in 3D space that represents the geometry of the
chromosome. It consists of at least two points: one for the first ID in the chromosome and
one for the last ID in the chromosome. It can have an arbitrary number of points between, 
and these can be at an arbitrary spacing. 

This series of points is typically represented as a curve constrained by the points, or as
a series of line segments.

```
id,x,y,z
int,float,float,float
int,float,float,float
...
int,float,float,float
```

## point arrays 

A point array file is named `pointXXX.csv`, where `XXX` is a unique identifier.
A point array file consists of an `id` column, and any number of named columns.
The `id` value is an id of a point along the genome. 
The named columns are values at that point.

```
point.csv

id,varname,varname,varname
int,float,float,float
...
int,float,float,float
```

## peak arrays 

A peak array file is named `peakXXX.csv`, where `XXX` is a unique identifier. 
A peak array file consists of two `id` columns, and any number of named columns.
The `id` value is an id of a point along the genome. 
The values are 0 at each `id`, and `float` at the midpoint between the two ids.

The named columns are values at the midpoint between the two  

```
peak.csv

id,id,varname,varname,varname
int,int,float,float,float
...
int,int,float,float,float
```
## metadata files

**chromosome**

```
begin: int
end:   int
genes:
    name,
    name,
    ...
    
    
```
