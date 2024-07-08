import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogHandler(FileSystemEventHandler):
    def __init__(self, base_path, callback):
        self.base_path = base_path
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            print(f"File modified: {event.src_path}")
            self.callback(event.src_path)

def extract_info(log_content):
    result_match = re.search(r"Node: ([\d.]+) has final result: ([-\d.]+)", log_content)
    time_match = re.search(r"Node: [\d.]+ took ([\d.]+) seconds", log_content)
    transmissions_match = re.search(r"Node: [\d.]+ needed (\d+) transmissions", log_content)
    
    node_ip = result_match.group(1) if result_match else None
    result = float(result_match.group(2)) if result_match else None
    execution_time = float(time_match.group(1)) if time_match else None
    transmissions = int(transmissions_match.group(1)) if transmissions_match else None
    
    return node_ip, result, execution_time, transmissions

class ResultAggregator:
    def __init__(self, base_path):
        self.base_path = base_path
        self.results = {}
        self.run_counter = {}

    def process_file(self, file_path):
        print(f"Processing file: {file_path}")
        folder = os.path.basename(os.path.dirname(file_path))
        with open(file_path, 'r') as file:
            content = file.read()
            node_ip, result, time, transmissions = extract_info(content)
            if node_ip is not None and result is not None and time is not None and transmissions is not None:
                if folder not in self.results:
                    self.results[folder] = {}
                    self.run_counter[folder] = {}
                if node_ip not in self.results[folder]:
                    self.results[folder][node_ip] = []
                    self.run_counter[folder][node_ip] = 0
                
                self.run_counter[folder][node_ip] += 1
                run_number = self.run_counter[folder][node_ip]
                
                self.results[folder][node_ip].append({
                    'run': run_number,
                    'result': result,
                    'execution_time': time,
                    'transmissions': transmissions
                })
                
                self.display_update(folder, node_ip, run_number)
            else:
                print(f"Incomplete data found in {file_path}")
                print(f"Node IP: {node_ip}, Result: {result}, Time: {time}, Transmissions: {transmissions}")

    def display_update(self, folder, node_ip, run):
        print(f"\nUpdate in Folder {folder}:")
        print(f"  Node {node_ip}:")
        info = self.results[folder][node_ip][-1]
        print(f"    Run {run}:")
        print(f"      Final Result: {info['result']}")
        print(f"      Execution Time: {info['execution_time']:.2f} seconds")
        print(f"      Transmissions: {info['transmissions']}")

    def display_final_results(self):
        if not self.results:
            print("No results collected. Make sure the log files are being updated.")
            return
        for folder, folder_results in sorted(self.results.items()):
            print(f"\nFolder {folder}:")
            for node_ip, node_runs in sorted(folder_results.items()):
                print(f"  Node {node_ip}:")
                for run in node_runs:
                    print(f"    Run {run['run']}:")
                    print(f"      Final Result: {run['result']}")
                    print(f"      Execution Time: {run['execution_time']:.2f} seconds")
                    print(f"      Transmissions: {run['transmissions']}")

def main():
    base_path = "/home/leo/Documents/logs"
    aggregator = ResultAggregator(base_path)

    # Process existing files
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.txt'):
                aggregator.process_file(os.path.join(root, file))

    event_handler = LogHandler(base_path, aggregator.process_file)
    observer = Observer()
    observer.schedule(event_handler, base_path, recursive=True)
    observer.start()

    print(f"Monitoring log files in {base_path}. Press 'q' to quit and display final results.")
    
    try:
        while True:
            if input() == 'q':
                break
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        
    print("\nFinal Results:")
    aggregator.display_final_results()

if __name__ == "__main__":
    main()