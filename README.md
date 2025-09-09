# episcope

A tool for exploration of epigenetic datasets

|![application](doc/img/episcope.png)|
| ---- |
|*Screen capture of the episcope tool, showing visualizations of four chromosomes from an experiment.*|


## Prerequisites

- A recent (5.13+) version of ParaView

## Installing

Create a python virtual environment with a Python version matching the
`pvpython` version:
- Paraview `5.13` ships with Python `3.10`.
- Paraview `6.0` ships with Python `3.12`.

We will install the app and its dependencies in this virtual environment.

```bash
# Create the virtual environment (check the appropriate python version, see above)
python3 -m venv .venv --python=3.10

# Activate it
source .venv/bin/activate

# Install the app from PyPI
pip install episcope

# Deactivate the virtual environment
deactivate
```

## Running

Finally, start the application using the `pvpython` already present on your
machine

```bash
pvpython --venv .venv -m episcope.app --data /path/to/dataset
```

## Development

Clone this repository and `cd` into it:

```bash
git clone git@github.com:epicsuite/episcope.git

# or if without ssh:
# git clone https://github.com/epicsuite/episcope.git

cd episcope
```

Follow the same instructions as above, with the exception that the `episcope` package should be installed from local source:
```bash
# Install the app in editable mode
pip install -e .
```
