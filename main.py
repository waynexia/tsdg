import argparse
import csv
import yaml
import itertools
from functools import reduce
from pathlib import Path
import datetime
from tqdm import trange
import snappy

from proto.remote_pb2 import WriteRequest
from proto.types_pb2 import TimeSeries, Label, Sample

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
    parser.add_argument("-o", "--csvout", help="generate csv output file")
    parser.add_argument("--promout", help="generate remote write protobuf data")
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
def generate_csv_data(
    start: int,
    end: int,
    interval: int,
    precision: int,
    tags: list,
    fields: list,
    csv_out: str,
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
        csv_out (str): Output file for the generated CSV file.
    """
    with open(csv_out, "w", newline="") as output:
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

# Generate time-series data based on configuration
def generate_prom_data(
    start: int,
    end: int,
    interval: int,
    precision: int,
    tags: list,
    fields: list,
    prom_out: str,
):
    """
    Generates time-series data based on the provided configuration and writes it as binary remote write protobuf data compressed with snappy.
    Args:
        start (int): Start time in UNIX timestamp.
        end (int): End time in UNIX timestamp.
        interval (int): Time interval between data points.
        precision (int): Precision of the timestamp.
        tags (list): List of tag definitions.
        fields (list): List of field definitions.
        prom_out (str): Output file for the generated CSV file.
    """
    BATCH_SIZE = 10000000
    accum_size = 0
    file_index = 0
    total_counter = 0
    time_series = []
    time_slice = 5 * 60 ## 5 mins

    tags_permutation = tag_set_permutation(tags)
    series_generator = [
        [series, dict([[field.name, field.dist.generator()] for field in fields])]
        for series in tags_permutation
    ]

    ## open writer from file index 0
    writer = open(prom_file(prom_out, file_index), 'wb')

    ## split timestamp into slice
    for slice_start in trange(start, end, time_slice):

        ## for each tag combination
        for series in series_generator:
            labels = {}

            ## assign tags
            for (label_name, label_value) in series[0].items():
                labels[label_name] = label_value

            ## for each metric
            for (field, field_gen) in series[1].items():
                ## set metric name
                labels['__name__'] = field
                ## reset sample array
                samples = []

                ## generate full time series
                for ts in range(slice_start, slice_start+time_slice, interval):
                    timestamp = ts * precision
                    value = next(field_gen)
                    samples.append((timestamp, value))
                    accum_size += 1

                time_series.append(build_timeseries(labels, samples))

                ## flush to file and start a new file
                if accum_size >= BATCH_SIZE:
                    write_request = build_remote_write_message(time_series)
                    writer.write(write_request)
                    writer.close()

                    ## open new file
                    file_index += 1
                    writer = open(prom_file(prom_out, file_index), 'wb')
                    ## reset counters
                    total_counter += accum_size
                    accum_size = 0
                    time_series = []

    write_request = build_remote_write_message(time_series)
    writer.write(write_request)
    writer.close()

    total_counter += accum_size
    print(f"Total samples generated: {total_counter}")


def prom_file(name: str, index: int) -> str:
    return f"{name}-{index}.bin"


def build_timeseries(labels: dict[str, str], samples: list[tuple[int, float]]) -> TimeSeries:
    time_series = TimeSeries()

    for (key, value) in labels.items():
        time_series.labels.append(Label(name=key, value=value))

    for (timestamp, value) in samples:
        time_series.samples.append(Sample(value=value, timestamp=timestamp))

    return time_series

def build_remote_write_message(timeseries: list[TimeSeries]) -> bytes:
    write_request = WriteRequest()
    write_request.timeseries.extend(timeseries)
    serialized_message = write_request.SerializeToString()
    compressed_message = snappy.compress(serialized_message)

    return compressed_message

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

    if args.csvout is not None:
        generate_csv_data(
            start=start,
            end=end,
            interval=interval,
            precision=precision,
            tags=tags,
            fields=fields,
            csv_out=args.csvout,
        )

    if args.promout is not None:
        generate_prom_data(
            start=start,
            end=end,
            interval=interval,
            precision=precision,
            tags=tags,
            fields=fields,
            prom_out=args.promout,
        )

if __name__ == "__main__":
    main()
