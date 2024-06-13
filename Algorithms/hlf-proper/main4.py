import sys
import node
import threading
import time
import datetime
import re
import socket

class processVirtualization(threading.Thread):
    def __init__(self, agent):
        threading.Thread.__init__(self)
        self.agent = agent
    def run(self):
        self.agent.start()

def main():
    receivedNum = 0
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "0.0.0.0"
    port = 12345
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Server listening...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Got connection from {addr}")

        data = client_socket.recv(1024).decode()
        try:
            receivedNum = float(data)
            print(f"Received number: {receivedNum}")
            client_socket.close()
            break
        except ValueError:
            print(f"Invalid data received: {data}")
            client_socket.close()

    nodeValues = [receivedNum, 600, -586, 400, 100, 100, -895, 10]
    nodeIPs = ["10.0.19.20", "10.0.19.21", "10.0.7.20", "0.0.0.0", "10.0.8.21", "10.0.0.25", "10.0.0.26", "10.0.0.27"]
    algorithm = 1
    topology = 6
    nrOfIterations = 10

    if topology == 6:
        node4 = node.Node2(nodeIPs[0], 9999, nodeValues[0], [nodeIPs[i] for i in [1]], algorithm, nrOfIterations)
        print("Creating nodeIP: %s with value %d on Port %d" % (node4.HOST, node4.VALUE, node4.PORT))
        print("Node creation complete")

        # Notify main13 that node 4 is ready
        notify_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        notify_socket.connect(("10.0.19.21", 12346))
        notify_socket.sendall(b"node4_ready")
        notify_socket.close()

        # Wait for start signal from main13
        start_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        start_socket.bind((host, 12347))
        start_socket.listen(1)
        print("Waiting for start signal from main13...")
        client_socket, addr = start_socket.accept()
        start_signal = client_socket.recv(1024).decode()
        print(f"Received start signal: {start_signal}")
        if start_signal == "start":
            processVirtualization(node4).start()

if __name__ == "__main__":
    main()
