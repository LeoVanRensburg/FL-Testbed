#!/opt/core/venv/bin/python3

import os
import json
import re
from glob import glob
import time

def parse_node_values():
    node_values = {}
    current_time = time.time()
    five_minutes_ago = current_time - 300  # 300 seconds = 5 minutes

    for node_num in range(1, 7):
        log_path = f"/home/leo/Documents/logs/{node_num}/*"
        log_files = glob(log_path)
        
        node_values[f"node_{node_num}"] = None  # Initialize with None
        
        if log_files:
            # Filter files modified in the last 5 minutes
            recent_logs = [f for f in log_files if os.path.getmtime(f) > five_minutes_ago]
            
            if recent_logs:
                latest_log = max(recent_logs, key=os.path.getmtime)
                with open(latest_log, 'r') as file:
                    for line in file:
                        # Match any IP address followed by "has final result:"
                        match = re.search(r'Node: (\d+\.\d+\.\d+\.\d+) has final result: ([\d.]+)', line)
                        if match:
                            node_values[f"node_{node_num}"] = float(match.group(2))
                            break
    
    return json.dumps({"node_values": node_values})

if __name__ == "__main__":
    print(parse_node_values())