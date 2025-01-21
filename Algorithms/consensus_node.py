import socket
import threading
import json
import time
import select
import sys
import numpy as np
from typing import Dict, Set, List, Union, Tuple
from numpy.typing import NDArray

# Custom JSON encoder/decoder for numpy arrays
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return {"__ndarray__": obj.tolist()}
        return super().default(obj)

def numpy_decoder(dct):
    if "__ndarray__" in dct:
        return np.array(dct["__ndarray__"])
    return dct

# Define multiple topologies
STAR_TOPOLOGY = {
    1: {  # Central node
        2: '10.0.0.21',
        3: '10.0.0.22',
        4: '10.0.0.23',
        5: '10.0.0.24'
    },
    2: {
        1: '10.0.0.20',
        3: '10.0.0.22',
        4: '10.0.0.23',
        5: '10.0.0.24'
    },
    3: {
        1: '10.0.0.20',
        2: '10.0.0.21',
        4: '10.0.0.23',
        5: '10.0.0.24'
    },
    4: {
        1: '10.0.0.20',
        2: '10.0.0.21',
        3: '10.0.0.22',
        5: '10.0.0.24'
    },
    5: {
        1: '10.0.0.20',
        2: '10.0.0.21',
        3: '10.0.0.22',
        4: '10.0.0.23'
    }
}

TREE_TOPOLOGY = {
    1: {
        2: '10.0.0.21',
        3: '10.0.1.21'
    },
    2: {
        1: '10.0.0.20'
    },
    3: {
        1: '10.0.1.20',
        4: '10.0.2.21',
        5: '10.0.3.21'
    },
    4: {
        3: '10.0.2.20'
    },
    5: {
        3: '10.0.3.20'
    }
}

MESH_TOPOLOGY = {
    1: {  # Central node
        2: '10.0.0.21',
        3: '10.0.1.21',
        4: '10.0.2.21',
        5: '10.0.3.21'
    },
    2: {
        1: '10.0.0.20',
        3: '10.0.4.21',
        4: '10.0.6.21',
        5: '10.0.5.21'
    },
    3: {
        1: '10.0.1.20',
        2: '10.0.4.20',
        4: '10.0.7.21',
        5: '10.0.9.21'
    },
    4: {
        1: '10.0.2.20',
        2: '10.0.6.20',
        3: '10.0.7.20',
        5: '10.0.8.21'
    },
    5: {
        1: '10.0.3.20',
        2: '10.0.5.20',
        3: '10.0.9.20',
        4: '10.0.8.20'
    }
}

HLF_TOPOLOGY = {
    1: {  # Central node
        2: '10.0.0.21',
        3: '10.0.1.21',
        4: '10.0.5.21'
    },
    2: {
        1: '10.0.0.20',
        3: '10.0.2.20',
        4: '10.0.3.21'
    },
    3: {
        1: '10.0.1.20',
        2: '10.0.2.21',
        4: '10.0.4.21'
    },
    4: {
        1: '10.0.5.20',
        2: '10.0.3.20',
        3: '10.0.4.20',
        13: '10.0.19.21'
    },
    5: {
        6: '10.0.6.21',
        7: '10.0.9.21',
        8: '10.0.11.20'
    },
    6: {
        5: '10.0.6.20',
        7: '10.0.10.21',
        8: '10.0.7.21'
    },
    7: {
        5: '10.0.9.20',
        6: '10.0.10.20',
        8: '10.0.8.20',
        13: '10.0.18.21'
    },
    8: {
        5: '10.0.11.21',
        6: '10.0.7.20',
        7: '10.0.8.21'
    },
    9: {
        10: '10.0.12.21',
        11: '10.0.15.20',
        12: '10.0.17.20',
        13: '10.0.20.21'
    },
    10: {
        9: '10.0.12.20',
        11: '10.0.16.20',
        12: '10.0.13.21'
    },
    11: {
        9: '10.0.15.21',
        10: '10.0.16.21',
        12: '10.0.14.20'
    },
    12: {
        9: '10.0.17.21',
        10: '10.0.13.20',
        11: '10.0.14.21'
    },
    13: {
        4: '10.0.19.20',
        7: '10.0.18.20',
        9: '10.0.20.20'
    }
}

TOPOLOGIES = {
    'star': STAR_TOPOLOGY,
    'tree': TREE_TOPOLOGY,
    'mesh': MESH_TOPOLOGY,
    'hlf' : HLF_TOPOLOGY,
}

class ConsensusNode:
    def __init__(self, node_id: int, initial_value: NDArray[np.float64], host_ips: list, port: int, neighbors: Dict[int, tuple]):
        self.node_id = node_id
        self.value = initial_value
        self.host_ips = host_ips
        self.port = port
        self.neighbors = neighbors
        self.received_values: Dict[int, float] = {}
        self.running = True
        self.iteration = 0
        self.max_iterations = 20
        self.lock = threading.Lock()
        self.ready_neighbors: Set[int] = set()
        self.all_neighbors_ready = threading.Event()
        self.consensus_started = False
        self.message_buffer: Dict[int, Dict[int, NDArray[np.float64]]] = {}
        self.iteration_time = 2
        self.start_time = None
        self.server_sockets = []

    def start(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.daemon = True
        server_thread.start()

        time.sleep(2)
        print(f"Node {self.node_id} checking for neighbor readiness...")
        self.check_neighbors_ready()
        print(f"Node {self.node_id} waiting for all neighbors to be ready...")
        self.all_neighbors_ready.wait()
        print(f"Node {self.node_id} - All neighbors are ready!")

        current_time = time.time()
        next_twenty_seconds = current_time - (current_time % 20) + 20
        wait_time = next_twenty_seconds - current_time
        print(f"Node {self.node_id} will start consensus at {time.strftime('%H:%M:%S', time.localtime(next_twenty_seconds))}")
        print(f"Waiting for {wait_time:.2f} seconds...")

        time.sleep(wait_time - 0.1)
        while time.time() < next_twenty_seconds:
            pass

        self.consensus_started = True
        self.run_consensus()

    def run_server(self):
        for host_ip in self.host_ips:
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((host_ip, self.port))
                server_socket.listen(len(self.neighbors) + 1)
                self.server_sockets.append(server_socket)
                print(f"Node {self.node_id} listening on {host_ip}:{self.port}")
            except Exception as e:
                print(f"Failed to bind to {host_ip}:{self.port} - {e}")

        print(f"Connected to neighbors: {list(self.neighbors.keys())}")

        while self.running:
            try:
                readable, _, _ = select.select(self.server_sockets, [], [], 1.0)
                for sock in readable:
                    client_socket, addr = sock.accept()
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                    client_thread.daemon = True
                    client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"Server error: {e}")
                break

        for sock in self.server_sockets:
            sock.close()

    def check_neighbors_ready(self):
        for neighbor_id, neighbor_addr in self.neighbors.items():
            thread = threading.Thread(
                target=self.send_ready_check,
                args=(neighbor_id, neighbor_addr)
            )
            thread.daemon = True
            thread.start()

    def send_ready_check(self, neighbor_id: int, neighbor_addr: tuple):
        while not self.all_neighbors_ready.is_set():
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.settimeout(5)
                client_socket.connect(neighbor_addr)
                message = {
                    'type': 'ready_check',
                    'node_id': self.node_id
                }
                client_socket.send(json.dumps(message, cls=NumpyEncoder).encode())
                client_socket.close()

                with self.lock:
                    self.ready_neighbors.add(neighbor_id)
                    if len(self.ready_neighbors) == len(self.neighbors):
                        self.all_neighbors_ready.set()
                        return
            except Exception:
                time.sleep(2)
            finally:
                client_socket.close()

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(1024).decode()
            message = json.loads(data, object_hook=numpy_decoder)
            if message.get('type') == 'ready_check':
                with self.lock:
                    self.ready_neighbors.add(message['node_id'])
                    if len(self.ready_neighbors) == len(self.neighbors):
                        self.all_neighbors_ready.set()
                response = {
                    'type': 'ready_response',
                    'node_id': self.node_id
                }
                client_socket.send(json.dumps(response, cls=NumpyEncoder).encode())
            elif self.consensus_started:
                with self.lock:
                    sender_id = message['node_id']
                    value = message['value']
                    msg_iteration = message['iteration']
                    if msg_iteration not in self.message_buffer:
                        self.message_buffer[msg_iteration] = {}
                    self.message_buffer[msg_iteration][sender_id] = value
                    print(f"\033[94m← Node {self.node_id} received value {np.round(value, 4).astype(str)} "
                          f"from node {sender_id} (iteration {msg_iteration})\033[0m")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def send_value_to_neighbor(self, neighbor_id: int, neighbor_addr: tuple):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.settimeout(5)
                client_socket.connect(neighbor_addr)
                message = {
                    'node_id': self.node_id,
                    'value': self.value,
                    'iteration': self.iteration
                }
                client_socket.send(json.dumps(message, cls=NumpyEncoder).encode())
                print(f"\033[92m→ Node {self.node_id} sent value {np.round(self.value, 4).astype(str)} to node {neighbor_id}\033[0m")
                client_socket.close()
                return
            except Exception as e:
                print(f"\033[91m× Node {self.node_id} failed to send to node {neighbor_id}: {e}\033[0m")
                if attempt == max_retries - 1:
                    print(f"Failed to send value to neighbor {neighbor_id} after {max_retries} attempts")
            finally:
                client_socket.close()

    def run_consensus(self):
        print(f"\n=== Node {self.node_id} starting consensus with initial value: {self.value.astype(str)} ===\n")
        self.start_time = time.time() + (10 - (time.time() % 10))
        while self.iteration < self.max_iterations:
            iteration_start = self.start_time + (self.iteration * self.iteration_time)
            wait_time = iteration_start - time.time()
            if wait_time > 0:
                time.sleep(wait_time)
            print(f"\n--- Node {self.node_id} Iteration {self.iteration} ---")
            print(f"Current value: {np.round(self.value, 4).astype(str)}")
            for neighbor_id, neighbor_addr in self.neighbors.items():
                self.send_value_to_neighbor(neighbor_id, neighbor_addr)
            print(f"\nNode {self.node_id} waiting for neighbor values...")
            deadline = iteration_start + (self.iteration_time * 0.8)
            while time.time() < deadline:
                with self.lock:
                    if self.iteration in self.message_buffer:
                        current_messages = self.message_buffer[self.iteration]
                        if len(current_messages) >= len(self.neighbors):
                            break
                time.sleep(0.1)
            with self.lock:
                if self.iteration in self.message_buffer:
                    received_values = self.message_buffer[self.iteration]
                    all_values = [self.value] + list(received_values.values())
                    print(f"\nNode {self.node_id} Summary for Iteration {self.iteration}:")
                    print(f"Own value: {np.round(self.value, 4).astype(str)}")
                    print("Received values:")
                    for node_id, value in received_values.items():
                        print(f"  From Node {node_id}: {np.round(value, 4).astype(str)}")
                    old_value = self.value.copy()
                    self.value = sum(all_values) / len(all_values)
                    print(f"\nNew average: {np.round(self.value, 4).astype(str)}")
                    print(f"Value change: {np.round(self.value - old_value, 4).astype(str)}")
                    del self.message_buffer[self.iteration]
            self.iteration += 1
        print(f"\n=== Node {self.node_id} finished with consensus value: {np.round(self.value, 4).astype(str)} ===\n")
        self.running = False

def get_node_listening_ips(node_id: int, topology_with_ips: dict) -> list:
    listening_ips = set()
    for other_node_connections in topology_with_ips.values():
        if node_id in other_node_connections:
            listening_ips.add(other_node_connections[node_id])
    return list(listening_ips)

def run_node(node_id: int, initial_value: NDArray[np.float64], port: int, network_topology_with_ips: dict):
    host_ips = get_node_listening_ips(node_id, network_topology_with_ips)
    print(f"Node {node_id} will listen on its IP addresses: {host_ips}")

    neighbors = {}
    if node_id in network_topology_with_ips:
        for neighbor_id, neighbor_ip in network_topology_with_ips[node_id].items():
            neighbors[neighbor_id] = (neighbor_ip, port)
    print(f"Node {node_id} will connect to neighbors: {neighbors}")

    node = ConsensusNode(
        node_id=node_id,
        initial_value=initial_value,
        host_ips=host_ips,
        port=port,
        neighbors=neighbors
    )
    node.start()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 consensus.py <topology> <node_id>")
        print(f"Available topologies: {', '.join(TOPOLOGIES.keys())}")
        sys.exit(1)

    try:
        topology = sys.argv[1]
        node_id = int(sys.argv[2])

        if topology not in TOPOLOGIES:
            print(f"Invalid topology. Choose from: {', '.join(TOPOLOGIES.keys())}")
            sys.exit(1)

        CURRENT_TOPOLOGY_WITH_IPS = TOPOLOGIES[topology]

        if node_id not in CURRENT_TOPOLOGY_WITH_IPS and not any(node_id in connections
                for connections in CURRENT_TOPOLOGY_WITH_IPS.values()):
            print(f"Invalid node ID: {node_id}")
            print(f"Valid node IDs are: {sorted(set().union(*[{k} | set(v.keys()) for k, v in CURRENT_TOPOLOGY_WITH_IPS.items()]))}")
            sys.exit(1)

        # Node initial values (now using vectors)
        NODE_VALUES = {
            1: np.array([10.0, 20.0, 30.0]),
            2: np.array([600.0, 300.0, 400.0]),
            3: np.array([-586.0, -200.0, -300.0]),
            4: np.array([400.0, 500.0, 600.0]),
            5: np.array([100.0, 200.0, 300.0]),
            6: np.array([10.0, 20.0, 30.0]),
            7: np.array([600.0, 300.0, 400.0]),
            8: np.array([-586.0, -200.0, -300.0]),
            9: np.array([400.0, 500.0, 600.0]),
            10: np.array([10.0, 20.0, 30.0]),
            11: np.array([600.0, 300.0, 400.0]),
            12: np.array([-586.0, -200.0, -300.0]),
            13: np.array([400.0, 500.0, 600.0])
        }

        PORT = 5001

        if node_id not in NODE_VALUES:
            print(f"No initial value defined for node {node_id}")
            sys.exit(1)

        print(f"Starting node {node_id} with {topology} topology...")
        run_node(node_id, NODE_VALUES[node_id], PORT, CURRENT_TOPOLOGY_WITH_IPS)

    except ValueError:
        print("Node ID must be an integer")
        sys.exit(1)
