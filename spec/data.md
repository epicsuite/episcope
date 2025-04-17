# Data specification

## genome

A genome is the genetic information for an organism. It is a sequence of nucleotides of
(in our case) DNA, made up of base pairs of adenine, cytosine, guanine and thymine.

A genome is typically represented by a linear sequence of base pairs. Each base pair has
a unique ID that is its position along the linear sequence.

The IDs of a genome is a 1-based sequence of numbers.

## chromosome

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

## variable arrays

Variables are represented by `.csv` files, named by the type of data in the array.

```
point.csv

id,varname
int,float
...
int,float
```

```
peak.csv

id,id,id,varname,varname,varname
int,int,int,float,float,float
...
int,int,int,float,float,float
```
