import argparse
import copy
import yaml
import itertools
import multiprocessing
from functools import reduce
from pathlib import Path
import datetime
from tqdm import trange
import snappy

from proto.remote_pb2 import WriteRequest
from proto.types_pb2 import TimeSeries, Label, Sample

from col import Column
from distribution import Random
from counter import Counter

BATCH_SIZE = 10000000
PRECISION = 1000
TIME_SLICE = 2 * 60 ## 2 mins


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
    parser.add_argument("--promout", help="generate remote write protobuf data")
    parser.add_argument("-c", "--config", default="./config.yaml", help="config file")
    parser.add_argument("-j", "--parallelism", default=1, help="Parallelism when generating data")
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
def generate_prom_data(
    start: int,
    end: int,
    interval: int,
    base_metrics: dict,
    tags: list,
    fields: dict,
    prom_out: str,
    parallelism: int,
):
    """
    Generates time-series data based on the provided configuration and writes it as binary remote write protobuf data compressed with snappy.
    Args:
        start (int): Start time in UNIX timestamp.
        end (int): End time in UNIX timestamp.
        interval (int): Time interval between data points.
        precision (int): Precision of the timestamp.
        base_metrics (list): The base prometheus metrics to generate from
        tags (list): Additional tags definitions.
        fields (dict): dict of field definitions.
        prom_out (str): Output file for the generated CSV file.
    """
    file_index_counter = Counter(-1)
    total_counter = Counter(0)

    tags_permutation = tag_set_permutation(tags)

    ## we will start from build all time-series and value generators
    ## the items in this list are tuple of (labels, fieldgen)
    all_series = []
    for series in tags_permutation:
        parent_labels = {}
        parent_labels.update(series)

        for (field, metrics_base_labels) in base_metrics.items():

            for base_labels in metrics_base_labels:
                time_series_labels = copy.copy(parent_labels)

                field_def = fields.get(field)
                if field_def is not None:
                    field_gen = field_def.dist.generator()
                else:
                    field_gen = Random(0, 100).generator()

                time_series_labels['__name__'] = field
                time_series_labels.update(base_labels)

                all_series.append((time_series_labels, field_gen))

    ## print a summary of time_series
    print(f"Total number of time series {len(all_series)}")

    series_parts = split_into_n_parts(all_series, parallelism)
    handles = []
    for i in range(parallelism):
        handle = multiprocessing.Process(target=generate_data_for_series, args=(series_parts[i], file_index_counter, total_counter, start, end, interval, prom_out))
        handle.start()
        handles.append(handle)

    for handle in handles:
        handle.join()

    print(f"Total samples generated: {total_counter.value()}")

def generate_data_for_series(series, file_index_counter, total_counter, start, end, interval, prom_out):
    ## working set
    time_series = []
    accum_size = 0
    ## open writer from file index 0
    writer = open(prom_file(prom_out, file_index_counter.incr(1)), 'wb')
    ## split timestamp into slice
    for slice_start in trange(start, end, TIME_SLICE):

        ## for each time series
        for (labels, field_gen) in series:

            ## reset sample array
            samples = []

            ## generate full time series
            for ts in range(slice_start, slice_start+TIME_SLICE, interval):
                timestamp = ts * PRECISION
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
                writer = open(prom_file(prom_out, file_index_counter.incr(1)), 'wb')
                ## reset counters
                total_counter.incr(accum_size)
                accum_size = 0
                time_series = []

    total_counter.incr(accum_size)
    write_request = build_remote_write_message(time_series)
    writer.write(write_request)
    writer.close()

def split_into_n_parts(lst, n):
    """Split a list into n parts of approximately equal length."""
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

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
    if not fields:
        return []

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

    base_metrics = load_yaml(config['base'])
    print(f"Loaded base metrics: {len(base_metrics)}")
    tags = parse_col_defs(config["tags"])

    field_list = parse_col_defs(config["fields"])
    fields = {}
    for f in field_list:
        fields[f['name']] = f

    if args.promout is not None:
        generate_prom_data(
            start=start,
            end=end,
            interval=interval,
            base_metrics=base_metrics,
            tags=tags,
            fields=fields,
            prom_out=args.promout,
            parallelism=int(args.parallelism)
        )

if __name__ == "__main__":
    main()
