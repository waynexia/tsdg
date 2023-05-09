import argparse
import csv
import yaml
import itertools
from functools import reduce
import random
from pathlib import Path
import datetime
from tqdm import trange


# Parse command line arguments and return the parsed result
def arg_parser():
    parser = argparse.ArgumentParser(
        prog="tsdg", description="Time-Series Data Generator"
    )
    parser.add_argument("-o", "--out", default="./tsdg.csv", help="output file")
    parser.add_argument("-c", "--config", default="./config.yaml", help="config file")
    return parser.parse_args()


def tag_set_permutation(tag_set: dict):
    keys, values = zip(*tag_set.items())
    count = reduce(lambda count, i: count * len(i), values, 1)
    print("number of tag combinations:" + str(count))
    permutation = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return permutation


def generate_data(
    start: int,
    end: int,
    interval: int,
    precision: int,
    num_field: int,
    out_dir: str,
    tag_set: dict,
):
    with open(out_dir, "w", newline="") as output:
        writer = csv.writer(output, delimiter=",")
        tags_permutation = tag_set_permutation(tag_set)
        # write header
        header = (
            ["timestamp"]
            + [k for k in tag_set.keys()]
            + ["field" + str(i) for i in range(num_field)]
        )
        writer.writerow(header)
        # write rows
        for ts in trange(start, end, interval):
            for tags in tags_permutation:
                timestamp = ts * precision
                tag_array = [v for v in tags.values()]
                field_array = [random.random() * 100 for _ in range(num_field)]
                writer.writerow([timestamp] + tag_array + field_array)


# Load yaml file
def load_yaml(path):
    with open(path, "r") as file:
        config = yaml.safe_load(file)
        return config


# Parse rfc3339 timestamp to unix timestamp
def parse_time(time_str: str):
    return datetime.datetime.fromisoformat(time_str).timestamp()


def main():
    args = arg_parser()
    print(args)
    config_path = Path(args.config)
    config = load_yaml(config_path)
    generate_data(
        int(parse_time(
            config["start"],
        )),
        int(parse_time(config["end"])),
        int(config["interval"]),
        int(config["precision"]),
        config["num-field"],
        args.out,
        config["tag-set"],
    )


if __name__ == "__main__":
    main()
