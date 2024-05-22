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
    parser = argparse.ArgumentParser(
        prog="tsdg", description="Time-Series Data Generator"
    )
    parser.add_argument("-o", "--out", default="./tsdg.csv", help="output file")
    parser.add_argument("-c", "--config", default="./config.yaml", help="config file")
    return parser.parse_args()


def tag_set_permutation(tags: list):
    tag_set = {tag.name: [tag_v for tag_v in tag.dist.all()] for tag in tags}
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
    tags: list,
    fields: list,
    out_dir: str,
):
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
    with open(path, "r") as file:
        config = yaml.safe_load(file)
        return config


# Parse rfc3339 timestamp to unix timestamp
def parse_time(time_str: str) -> float:
    return datetime.datetime.fromisoformat(time_str).timestamp()


def parse_col_defs(fields: list) -> list:
    return [Column.from_config(f) for f in fields]


def main():
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
