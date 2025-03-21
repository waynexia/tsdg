import re
import requests
from collections import defaultdict
import os
import sys

# Function to parse OpenMetrics format and extract metric names, unique label keys, and unique label values
def parse_openmetrics(metrics_text):
    # Regex to match metric lines (metric name and labels)
    metric_pattern = re.compile(r'^(?P<metric_name>[a-zA-Z_:][a-zA-Z0-9_:]+)(?P<labels>\{[^}]+\})?\s+(?P<value>\S+)')

    metrics = defaultdict(lambda: defaultdict(set))

    for line in metrics_text.splitlines():
        # Skip comments and empty lines
        if line.startswith('#') or not line.strip():
            continue

        # Match the metric line
        match = metric_pattern.match(line)
        if match:
            metric_name = match.group('metric_name')
            labels = match.group('labels')

            # Parse labels if they exist
            if labels:
                # Extract label key-value pairs
                label_pairs = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)=["]([^"]*)["]', labels)
                for key, value in label_pairs:
                    metrics[metric_name][key].add(value)

    return metrics

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

        # Parse metrics
        metrics = parse_openmetrics(metrics_text)

        # Print results
        for metric_name, label_data in metrics.items():
            print(f"Metric: {metric_name}")
            if label_data:
                for label_key, label_values in label_data.items():
                    print(f"  Label Key: {label_key}")
                    print(f"    Unique Values: {', '.join(sorted(label_values))}")
            else:
                print("  No labels")
            print()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
