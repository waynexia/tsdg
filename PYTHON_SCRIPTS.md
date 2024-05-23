# Python Scripts Documentation

## Overview

This document provides an overview of the Python scripts used in the project, detailing their purpose, functionality, and how they interact with each other. It also mentions any external libraries used by the scripts and their role in the project.

## Scripts

### `col.py`

This script defines the `DataType` enum and the `Column` class. The `DataType` enum includes types such as INTEGER, STRING, and FLOAT, representing the data types supported in columns. The `Column` class represents a column in a dataset, including its name, data type, nullability, and distribution. It includes methods for initializing a column instance and creating a column instance from a configuration dictionary.

### `distribution.py`

This script contains the `Distribution` class and various distribution classes like `MonoInc`, `MonoDec`, `Random`, etc. The `Distribution` class serves as an abstract base class for distributions, defining the structure for distribution classes. Each distribution class implements a specific behavior for generating data points. The script also includes a method for selecting the appropriate distribution class based on configuration.

### `main.py`

The `main.py` script is the entry point of the project. It includes functions for parsing command line arguments, generating permutations of tag sets, generating time-series data based on configuration, loading YAML files, parsing RFC3339 timestamps, and parsing column definitions from configuration. The script orchestrates the workflow of generating time-series data using the configuration file.

## External Libraries

- `argparse`: Used for parsing command line arguments.
- `csv`: Utilized for writing the generated data to a CSV file.
- `pyyaml`: Employed for loading and parsing YAML configuration files.
- `tqdm`: Used for displaying progress bars during data generation.

