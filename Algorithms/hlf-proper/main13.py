import sys
import node
import threading
import time
import datetime
import socket

class processVirtualization(threading.Thread):
    def __init__(self, agent):
        threading.Thread.__init__(self)
        self.agent = agent
    def run(self):
        self.agent.start()

def main():
    # Capture the current time
    now = datetime.datetime.now()

    # Calculate the seconds to wait until the start of the next minute
    wait_seconds = 60 - now.second

    # Wait until the start of the next minute
    time.sleep(wait_seconds)
    
    # Capture the start time of the closest minute
    start_time = datetime.datetime.now()
    
    nodeValues = [10,600,-586,400, 100, 100, -895, 10]
    nodeIPs = ["0.0.0.0", "10.0.19.20", "10.0.18.20", "10.0.20.20", "10.0.3.21", "10.0.0.25", "10.0.0.26", "10.0.0.27"]
    algorithm = 1
    topology = 6
    nrOfIterations = 10
    ready_nodes = []
    
    node1 = node.Node2(nodeIPs[0], 9999, nodeValues[0], [nodeIPs[i] for i in [1,2,3]], algorithm, nrOfIterations)
    print("Creating nodeIP: %s with value %d on Port %d" % (node1.HOST, node1.VALUE, node1.PORT))
    print("Node creation complete")
    print("Starting")

    def listen_for_readiness():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = "0.0.0.0"
        port = 12346
        server_socket.bind((host, port))
        server_socket.listen(5)
        print("Listening for readiness signals...")
        while len(ready_nodes) < 3:
            client_socket, addr = server_socket.accept()
            data = client_socket.recv(1024).decode()
            ready_nodes.append(data)
            print(f"Node ready: {data}")
            client_socket.close()

    readiness_thread = threading.Thread(target=listen_for_readiness)
    readiness_thread.start()
    readiness_thread.join()

    if "node4_ready" in ready_nodes and "node7_ready" in ready_nodes and "node9_ready" in ready_nodes:
        for ip in ["10.0.19.20", "10.0.20.20", "10.0.18.20"]:
            start_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            start_socket.connect((ip, 12347))
            start_socket.sendall(b"start")
            start_socket.close()
        print("Start signals sent to nodes 4, 7, and 9.")

    node1.start()
    
    # Capture the end time after the program finishes
    end_time = datetime.datetime.now()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    # Print the elapsed time
    print(f"Elapsed time: {elapsed_time}")
    

if __name__ == "__main__":
    main()
