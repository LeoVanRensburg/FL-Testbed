import re
import json
import os
from datetime import datetime

# Base path to your logs directory
base_log_path = "/home/leo/Documents/logs"

# Reference value to compare against
reference_value = 104.8

# Initialize a list to store all data points
data_points = []

# Regex patterns
timestamp_pattern = r'\[(.*?)\]'  # Captures the timestamp within square brackets
iteration_pattern = r'\[.*?\] (\d+\.\d+\.\d+\.\d+).*iteration.*?(\d+)'
value_pattern = r'\[.*?\] (\d+\.\d+\.\d+\.\d+).*Value: (-?[\d\.]+)'

# Loop through node folders 1 to 5
for node_number in range(1, 6):
    log_file_path = os.path.join(base_log_path, str(node_number), 'log.txt')
    node_ip = None
    iterations = {}
    current_iteration = None

    # Check if the log file exists
    if not os.path.exists(log_file_path):
        continue

    # Open and read the log file
    with open(log_file_path, 'r') as f:
        for line in f:
            # Extract the timestamp
            timestamp_match = re.search(timestamp_pattern, line)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                # Try multiple timestamp formats
                for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%d/%b/%Y:%H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
                    try:
                        timestamp = datetime.strptime(timestamp_str, fmt)
                        break  # Successfully parsed timestamp
                    except ValueError:
                        continue
                else:
                    # Could not parse timestamp
                    continue
                iso_timestamp = timestamp.isoformat()
            else:
                continue  # Skip lines without a timestamp

            # Extract the node IP address if not already done
            if node_ip is None:
                ip_match = re.search(r'Creating nodeIP: (\d+\.\d+\.\d+\.\d+)', line)
                if ip_match:
                    node_ip = ip_match.group(1)

            # Check for the iteration line
            iteration_match = re.search(iteration_pattern, line)
            if iteration_match:
                ip_in_line = iteration_match.group(1)
                if ip_in_line == node_ip:
                    current_iteration = int(iteration_match.group(2))
                else:
                    current_iteration = None  # Reset if IP doesn't match
                continue

            # Check for the value line
            value_match = re.search(value_pattern, line)
            if value_match and current_iteration is not None:
                ip_in_line = value_match.group(1)
                if ip_in_line == node_ip:
                    value = float(value_match.group(2))
                    if reference_value != 0:
                        percent_diff = abs(((value - reference_value) / reference_value) * 100)
                    else:
                        percent_diff = float('inf')

                    # Store the value for the current timestamp if not already stored
                    key = (iso_timestamp, node_number)
                    if key not in iterations:
                        iterations[key] = percent_diff
                    # Reset current_iteration after processing
                    current_iteration = None
                else:
                    continue

    # After processing all lines, append the data points for this node
    for (iso_timestamp, node_num), percent_diff in sorted(iterations.items()):
        data_points.append({
            'time': iso_timestamp,
            'node': f"node_{node_num}",
            'percent_difference': percent_diff
        })

# Prepare the JSON output
print(json.dumps(data_points, indent=2))
