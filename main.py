import argparse
import csv
import yaml
import itertools
from functools import reduce
import random
from pathlib import Path
import datetime
from tqdm import trange

from col import Column

# Parse command line arguments and return the parsed result
def arg_parser():
    """
    Parses command line arguments for the script.

    Returns:
        argparse.Namespace: An object containing the parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="tsdg", description="Time-Series Data Generator"
    )
    parser.add_argument("-o", "--out", default="./tsdg.csv", help="output file")
    parser.add_argument("-c", "--config", default="./config.yaml", help="config file")
    return parser.parse_args()

# Generate permutations of tag sets
def tag_set_permutation(tags: list):
    """
    Generates all possible permutations of tag sets.

    Args:
        tags (list): A list of tags to generate permutations for.

    Returns:
        list: A list of dictionaries, each representing a permutation of tag sets.
    """
    tag_set = {tag.name: [tag_v for tag_v in tag.dist.all()] for tag in tags}
    keys, values = zip(*tag_set.items())
    count = reduce(lambda count, i: count * len(i), values, 1)
    print("number of tag combinations:" + str(count))
    permutation = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return permutation

# Generate time-series data based on configuration
def generate_data(
    start: int,
    end: int,
    interval: int,
    precision: int,
    tags: list,
    fields: list,
    out_dir: str,
):
    """
    Generates time-series data based on the provided configuration and writes it to a CSV file.

    Args:
        start (int): Start time in UNIX timestamp.
        end (int): End time in UNIX timestamp.
        interval (int): Time interval between data points.
        precision (int): Precision of the timestamp.
        tags (list): List of tag definitions.
        fields (list): List of field definitions.
        out_dir (str): Output directory for the generated CSV file.
    """
    with open(out_dir, "w", newline="") as output:
        writer = csv.writer(output, delimiter=",")
        # write header
        header = ["ts"] + [t.name for t in tags] + [f.name for f in fields]
        writer.writerow(header)
        tags_permutation = tag_set_permutation(tags)
        series_generator = [
            [series, dict([[field.name, field.dist.generator()] for field in fields])]
            for series in tags_permutation
        ]
        # write rows
        for ts in trange(start, end, interval):
            for series in series_generator:
                timestamp = ts * precision
                tag_array = [v for v in series[0].values()]
                field_array = [next(v) for v in series[1].values()]
                writer.writerow([timestamp] + tag_array + field_array)

# Load yaml file
def load_yaml(path):
    """
    Loads a YAML file and returns its content.

    Args:
        path (str): Path to the YAML file.

    Returns:
        dict: The content of the YAML file.
    """
    with open(path, "r") as file:
        config = yaml.safe_load(file)
        return config

# Parse RFC3339 timestamp to UNIX timestamp
def parse_time(time_str: str) -> float:
    """
    Parses an RFC3339 timestamp string to a UNIX timestamp.

    Args:
        time_str (str): The RFC3339 timestamp string.

    Returns:
        float: The UNIX timestamp.
    """
    return datetime.datetime.fromisoformat(time_str).timestamp()

# Parse column definitions from configuration
def parse_col_defs(fields: list) -> list:
    """
    Parses column definitions from the configuration.

    Args:
        fields (list): A list of field configurations.

    Returns:
        list: A list of Column objects.
    """
    return [Column.from_config(f) for f in fields]

# Main function
def main():
    """
    Main function of the script. Parses command line arguments, loads configuration,
    and generates time-series data based on the configuration.
    """
    args = arg_parser()
    print(args)
    config_path = Path(args.config)
    config = load_yaml(config_path)

    start = int(parse_time(config["start"]))
    end = int(parse_time(config["end"]))
    interval = int(config["interval"])
    precision = int(config["precision"])

    tags = parse_col_defs(config["tags"])
    fields = parse_col_defs(config["fields"])

    generate_data(
        start=start,
        end=end,
        interval=interval,
        precision=precision,
        tags=tags,
        fields=fields,
        out_dir=args.out,
    )

if __name__ == "__main__":
    main()
