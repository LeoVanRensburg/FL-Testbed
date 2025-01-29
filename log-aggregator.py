import os
import re
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            self.callback(event.src_path)

def parse_log_entry(line):
    timestamp_match = re.search(r'\[(.*?)\]', line)
    consensus_match = re.search(r"Node (\d+) finished with consensus value: \[(.*?)\]", line)
    
    if timestamp_match:
        timestamp = timestamp_match.group(1)
    else:
        timestamp = None

    if consensus_match:
        node_number = consensus_match.group(1)
        # Convert the consensus values string to a list of floats
        consensus_values = [float(x.strip().strip("'")) for x in consensus_match.group(2).split()]
        return {
            "timestamp": timestamp,
            "node_number": node_number,
            "type": "consensus",
            "value": consensus_values
        }
    else:
        return None

class ResultAggregator:
    def __init__(self, base_path):
        self.base_path = base_path
        self.results = {}

    def process_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                entry = parse_log_entry(line)
                if entry:
                    node_number = entry['node_number']
                    if node_number not in self.results:
                        self.results[node_number] = {}
                    self.results[node_number][entry['type']] = {
                        "timestamp": entry['timestamp'],
                        "value": entry['value']
                    }

    def get_results(self):
        return json.dumps(self.results)

def main():
    base_path = "/home/leo/Documents/logs"
    aggregator = ResultAggregator(base_path)
    
    # Process existing files
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.txt'):
                aggregator.process_file(os.path.join(root, file))

    event_handler = LogHandler(aggregator.process_file)
    observer = Observer()
    observer.schedule(event_handler, base_path, recursive=True)
    observer.start()

    try:
        while True:
            command = input("Enter 'q' to quit and display results, or press Enter to continue monitoring: ")
            if command.lower() == 'q':
                break
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()

    print(aggregator.get_results())

if __name__ == "__main__":
    main()
