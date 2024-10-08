from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import time
import os

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

PYTHON_PATH = "/opt/core/venv/bin/python3"
SCRIPTS = {
    "packet_loss": "packet_loss.py",
    "bandwidth": "bandwidth.py",
    "delay": "delay.py",
    "log_aggregator": "log-aggregator.py",
    "loss": "loss.py",
    "node_values": "/home/leo/Documents/DistributedConsensusAlgorithm/grafana/node-values.py",
    "difference": "difference.py"  # Added the difference script
}

@app.route('/execute/<script_name>', methods=['POST'])
def execute_script(script_name):
    if script_name not in SCRIPTS:
        return jsonify({"error": "Script not found"}), 404

    script_path = SCRIPTS[script_name]
    args = request.json.get('args', [])

    # Convert all arguments to strings
    args = [str(arg) for arg in args]

    try:
        result = subprocess.run(
            [PYTHON_PATH, script_path] + args,
            capture_output=True,
            text=True,
            check=True
        )

        # All our new scripts return JSON, so we can directly return their output
        output_json = json.loads(result.stdout)

        # If script_name is 'node_values' or 'difference', remove nodes with null values
        if script_name in ['node_values', 'difference'] and 'node_values' in output_json:
            output_json['node_values'] = {
                k: v for k, v in output_json['node_values'].items() if v is not None
            }

        return jsonify(output_json)
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Script execution failed",
            "output": e.stdout,
            "error_details": e.stderr
        }), 500
    except json.JSONDecodeError as e:
        return jsonify({
            "error": "Failed to parse JSON output from script",
            "output": result.stdout,
            "error_details": str(e)
        }), 500

@app.route('/start-simulation', methods=['POST'])
def start_simulation():
    try:
        # Start the simulation
        result = subprocess.run(
            ["/opt/core/venv/bin/python", "/home/leo/Documents/DistributedConsensusAlgorithm/Scenarios/Full-Mesh.py"],
            capture_output=True,
            text=True,
            check=True
        )

        # Wait for a short time to ensure the simulation has started
        time.sleep(5)

        # Kill session 1
        kill_command = "core-cli session -i 1 delete"
        kill_result = subprocess.run(
            kill_command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )

        return jsonify({
            "message": "Simulation started successfully and session 1 killed",
            "simulation_output": result.stdout,
            "kill_output": kill_result.stdout
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Simulation start or session kill failed",
            "output": e.stdout,
            "error_details": e.stderr
        }), 500

@app.route('/end-simulation', methods=['POST'])
def end_simulation():
    try:
        outputs = []
        for session_id in range(1, 7):
            command = f"core-cli session -i {8 - session_id} delete"
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            outputs.append(f"Session {session_id}: {result.stdout.strip()}")

        return jsonify({"message": "All simulation sessions ended successfully", "outputs": outputs})
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Failed to end all simulation sessions",
            "output": e.stdout,
            "error_details": e.stderr
        }), 500

@app.route('/attacks/loss', methods=['POST'])
def execute_loss_attack():
    try:
        data = request.json
        if not data or 'args' not in data or len(data['args']) != 4:
            return jsonify({"error": "Invalid input. Please provide four arguments."}), 400

        args = data['args']
        command = [
            "/opt/core/venv/bin/python3",
            "/home/leo/Documents/DistributedConsensusAlgorithm/loss.py",
            str(args[0]),  # Session ID
            str(args[1]),  # Topology
            str(args[2]),  # Nodes
            str(args[3])   # Packet Loss Percentage
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        return jsonify({
            "message": "Loss attack executed successfully",
            "output": result.stdout
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Loss attack execution failed",
            "output": e.stdout,
            "error_details": e.stderr
        }), 500

@app.route('/node-values', methods=['POST'])
def get_node_values():
    try:
        command = [
            PYTHON_PATH,
            SCRIPTS['node_values']
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        # Load the JSON output
        data = json.loads(result.stdout)

        # Remove nodes where value is null
        node_values = data.get('node_values', {})
        filtered_node_values = [
            {"node": k, "value": v}
            for k, v in node_values.items()
            if v is not None
        ]

        # Format data to match the desired output
        output_data = {
            "node_values": filtered_node_values
        }

        return jsonify(output_data)
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Node values retrieval failed",
            "output": e.stdout,
            "error_details": e.stderr
        }), 500

# New endpoints for Grafana integration
@app.route('/')
def index():
    return 'Grafana Simple JSON Datasource API'

@app.route('/search', methods=['POST'])
def search():
    # Return a list of available nodes
    metrics = [f"node_{i}" for i in range(1, 6)]  # Assuming nodes 1 to 5
    return jsonify(metrics)

@app.route('/query', methods=['POST'])
def query():
    req = request.get_json()
    results = []

    # Execute difference.py once
    try:
        result = subprocess.run(
            [PYTHON_PATH, SCRIPTS['difference']],
            capture_output=True,
            text=True,
            check=True
        )
        output_json = json.loads(result.stdout)
        nodes_data = output_json.get('nodes', {})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to execute difference.py", "details": e.stderr}), 500
    except json.JSONDecodeError as e:
        return jsonify({"error": "Failed to parse JSON output from difference.py", "details": str(e)}), 500

    for target in req.get('targets', []):
        target_node = target.get('target')
        data_points = []

        node_data = nodes_data.get(target_node, {})
        data_points_list = node_data.get('data_points', [])

        for data_point in data_points_list:
            value = data_point['percent_difference']
            timestamp = data_point['timestamp']
            data_points.append([value, timestamp])

        results.append({
            "target": target_node,
            "datapoints": data_points
        })

    return jsonify(results)

@app.route('/annotations', methods=['POST'])
def annotations():
    return jsonify([])

@app.route('/tag-keys', methods=['POST'])
def tag_keys():
    return jsonify([])

@app.route('/tag-values', methods=['POST'])
def tag_values():
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
