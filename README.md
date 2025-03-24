Time-Series Data Generator
--------------------------

# Usage

## Setup

This package uses `uv` to manage virtual environments.

After `uv` is installed, you can create a virtual environment by running the following command:

```script
uv venv
source .venv/bin/activate
uv sync
```

## Generate Data

Just run the main.py file with python3

```script
python main.py --promout <PATH>
```

Or add `--help` to see detailed parameters

```script
python main.py --help
```

# Configuration

`config.yaml` provides an example configuration file. You can change the parameters in the file to generate different time-series data.

# Python Scripts Documentation

For detailed information on the Python scripts used in this project, including their purpose, functionality, and how they interact with each other, please refer to the [PYTHON_SCRIPTS.md](PYTHON_SCRIPTS.md) document.
