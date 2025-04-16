# Data specification

## Genome

A genome is the genetic information for an organism. It is a sequence of nucleotides of
(in our case) DNA, made up of base pairs of adenine, cytosine, guanine and thymine.

A genome is typically represented by a linear sequence of base pairs. Each base pair has
a unique ID that is its position along the linear sequence.

The IDs of a genome is a 1-based sequence of numbers.

## Chromosome

A chromosome is a linear sequence of `n` base pairs in a genome. it is uniquely identified
by a begin and end ID along the genome sequence.

```
project/
    species/
    chr1/
        meta.json
        untreated/
            structure.csv
            001.csv
            001.csv
            ...
            nnn.csv
        infected/
        ...
        exp_001/
    chr2/
    ...
    chrn/
```


# structure.csv
The `structure.csv` file defines a line in 3D space that kkkkkkk

```
id,x,y,z
int,float,float,float
int,float,float,float
...
int,float,float,float
```
