import re
import requests
from collections import defaultdict
import os
import sys
import yaml

# Function to parse OpenMetrics format and extract unique label combinations
def parse_openmetrics(metrics_text):
    # Regex to match metric lines (metric name and labels)
    metric_pattern = re.compile(r'^(?P<metric_name>[a-zA-Z_:][a-zA-Z0-9_:]+)(?P<labels>\{[^}]+\})?\s+(?P<value>\S+)')

    metrics = defaultdict(set)

    for line in metrics_text.splitlines():
        # Skip comments and empty lines
        if line.startswith('#') or not line.strip():
            continue

        # Match the metric line
        match = metric_pattern.match(line)
        if match:
            metric_name = match.group('metric_name')
            labels = match.group('labels')

            # If labels exist, add them as a unique combination
            if labels:
                # Extract label key-value pairs and sort them for consistency
                label_pairs = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)=["]([^"]*)["]', labels)
                sorted_labels = tuple(sorted((key, value) for key, value in label_pairs))
                metrics[metric_name].add(sorted_labels)
            else:
                # No labels, add an empty tuple
                metrics[metric_name].add(tuple())

    return metrics

# Function to format label combinations as dictionaries
def format_label_combinations(metrics):
    formatted_metrics = {}
    for metric_name, label_combinations in metrics.items():
        if not label_combinations:
            formatted_metrics[metric_name] = None
            continue

        # Convert each label combination to a dictionary
        formatted_combinations = []
        for combo in label_combinations:
            formatted_combinations.append(dict(combo))
        formatted_metrics[metric_name] = formatted_combinations

    return formatted_metrics

# Fetch metrics from Prometheus Node Exporter
def fetch_metrics_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch metrics: {response.status_code}")

# Read metrics from a local file
def fetch_metrics_from_file(file_path):
    if not os.path.isfile(file_path):
        raise Exception(f"File not found: {file_path}")
    with open(file_path, 'r') as file:
        return file.read()

# Convert metrics data to YAML format
def metrics_to_yaml(metrics):
    yaml_data = {}
    for metric_name, label_data in metrics.items():
        yaml_data[metric_name] = {}
        if label_data:
            for label_key, label_values in label_data.items():
                yaml_data[metric_name][label_key] = sorted(label_values)
        else:
            yaml_data[metric_name] = None
    return yaml.dump(yaml_data, default_flow_style=False)

# Function to print a summary of metrics and time-series to stderr
def print_summary(metrics):
    total_metrics = len(metrics)
    total_time_series = sum(len(label_combinations) for label_combinations in metrics.values())

    print("\n=== Summary ===", file=sys.stderr)
    print(f"Total Metrics: {total_metrics}", file=sys.stderr)
    print(f"Total Time-Series (Unique Label Combinations): {total_time_series}", file=sys.stderr)

# Main function
def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <url_or_file>")
        sys.exit(1)

    input_arg = sys.argv[1]

    try:
        # Determine if the input is a URL or a file
        if input_arg.startswith('http'):
            metrics_text = fetch_metrics_from_url(input_arg)
        else:
            metrics_text = fetch_metrics_from_file(input_arg)

        # Parse metrics and extract unique label combinations
        metrics = parse_openmetrics(metrics_text)

        # Format label combinations as dictionaries
        formatted_metrics = format_label_combinations(metrics)

        # Convert to YAML format
        yaml_output = yaml.dump(formatted_metrics, default_flow_style=False)

        # Print YAML output
        print(yaml_output)

        # Print summary to stderr
        print_summary(metrics)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
