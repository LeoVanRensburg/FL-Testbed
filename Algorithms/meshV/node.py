import numpy as np
from utility import server
from phe import paillier
import sys
import socket
import time
import pickle
import random
import datetime

class Node():
    def __init__(self, HOST, PORT, VALUE, neighbors, algorithm, nrOfIterations):
        self.HOST = HOST
        self.PORT = PORT
        public_key, private_key = paillier.generate_paillier_keypair()
        self.PUBLIC = public_key
        self.PRIVATE = private_key
        self.VALUE = VALUE
        self.OLDVALUE = VALUE.copy() if isinstance(VALUE, np.ndarray) else VALUE
        self.neighbors = neighbors
        self.closedNeighbors = list(neighbors)
        self.closedNeighbors.append(HOST)
        self.whoKnowsWho = {}
        self.linkValues = {}
        self.yij = {}
        self.wij = {}       
        self.nrTransmissions = 0
        self.algorithm = algorithm
        self.nrOfIterations = nrOfIterations
        self.SYNC_DELAY = 0.1  # 100ms delay after synchronization

    def start(self):
        nodeServer = server.Server(self.HOST, self.PORT, self.VALUE, 1, self.neighbors, self.algorithm)
        nodeServer.start()

        time.sleep(1)

        start = time.time()

        try:
            if(self.algorithm == 1):
                self.computeSimple(nodeServer, self.neighbors)
            elif(self.algorithm == 2):
                self.computeNeighborhood(nodeServer)
        except Exception as e:
            print(f"Error in algorithm execution: {e}")
        finally:
            end = time.time()

            for i in self.neighbors:
                try:
                    self.sendClose(i)
                except Exception as e:
                    print(f"Error sending close to {i}: {e}")

            nodeServer.CLOSE = True
            while not nodeServer.CLOSED:
                time.sleep(0.1)
            nodeServer.join()

            print(f"Node: {self.HOST} has final result: {self.VALUE}")
            print(f"Node: {self.HOST} took {end-start} seconds")
            print(f"Node: {self.HOST} needed {self.nrTransmissions} transmissions")

    def send(self, neighbor, iteration, retry_limit=5):
        retry_count = 0
        while retry_count < retry_limit:
            try:
                cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cl.connect((neighbor, self.PORT))
                cl.sendall(str(iteration).encode())
                rec = cl.recv(1024)
                if rec == b'-1':
                    cl.close()
                    return np.array([-1])
                else:
                    data = pickle.loads(rec)
                    print(f"{self.HOST} has Value: {self.VALUE} and receives {data}")
                    self.nrTransmissions += 1
                    cl.close()
                    return data
            except Exception as e:
                print(f"Error in send: {e}")
                retry_count += 1
                time.sleep(1)
        print(f"Failed to send data to {neighbor} after {retry_limit} retries")
        return None

    def sendNeighborhoodEncryption(self, neighbor, encVal, weight, iteration):
        cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl.connect((neighbor, self.PORT))
        cl.sendall(b'average')
        data = cl.recv(1024)
        if(data == b'ack'):
            cl.sendall(str(iteration).encode())
            data = cl.recv(1024)
            if(data == b'big'):
                cl.close()
                return self.sendNeighborhoodEncryption(neighbor, encVal, weight, iteration)
            elif(data == b'ok'):
                data = pickle.dumps(str(self.PUBLIC.n))
                cl.sendall(data)
                data = cl.recv(1024)
                if(data == b'ack'):
                    data_val = pickle.dumps([str(v.ciphertext()) for v in encVal])
                    data_exp = pickle.dumps([str(v.exponent) for v in encVal])
                    cl.sendall(data_val)
                    data = cl.recv(1024)
                    cl.sendall(data_exp)
                    cl.recv(1024)
                    data = pickle.dumps(str(weight))
                    cl.sendall(data)
                    data_val = cl.recv(8192)
                    data_val = pickle.loads(data_val)
                    cl.sendall(b'ack')
                    data_exp = cl.recv(8192)
                    data_exp = pickle.loads(data_exp)
                    cl.close()
                    data = [paillier.EncryptedNumber(self.PUBLIC, int(v), int(e)) for v, e in zip(data_val, data_exp)]
                    self.nrTransmissions += 1
                    return data

    def sendNeighborhood(self, neighbor, mode):
        cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl.connect((neighbor, self.PORT))

        if mode == 1:
            data_string = pickle.dumps(self.closedNeighbors)
            cl.sendall(str(mode).encode())
            if(cl.recv(1024) == b'ok'):
                cl.sendall(data_string)
                self.nrTransmissions += 1
            cl.close()
        elif mode == 2:
            cl.sendall(str(mode).encode())
            if(cl.recv(1024) == b'ok'):
                cl.sendall(self.HOST.encode())
            if(cl.recv(1024) == b'ok'):
                cl.sendall(str(self.yij[neighbor]).encode())
                self.nrTransmissions += 1
            cl.close()

    def sendClose(self, neighbor):
        cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl.connect((neighbor, self.PORT))
        cl.sendall(b'close')
        print("Close send, received: " + str(cl.recv(1024)))
        cl.close()

    def wait_for_next_10_second_interval(self):
        current_time = time.time()
        next_interval = (current_time // 10 + 1) * 10
        time_to_wait = next_interval - current_time
        time.sleep(time_to_wait)
        # Add the small delay after synchronization
        time.sleep(self.SYNC_DELAY)

    def computeSimple(self, nodeServer, nrNeighbors):
        for i in range(1, self.nrOfIterations + 1):
            self.wait_for_next_10_second_interval()
            
            iteration_start = time.time()
            
            nodeServer.ITERATION = i
            print(f"{self.HOST} is in iteration: {i}")
            values = [self.VALUE]
            for j in self.neighbors:
                received_value = self.send(j, i)
                if received_value is not None and not np.array_equal(received_value, np.array([-1])):
                    values.append(received_value)
            
            self.OLDVALUE = self.VALUE.copy() if isinstance(self.VALUE, np.ndarray) else self.VALUE
            
            # Calculate mean only for valid values
            valid_values = [v for v in values if isinstance(v, np.ndarray)]
            if valid_values:
                self.VALUE = np.mean(valid_values, axis=0)
            else:
                print(f"Warning: No valid values received in iteration {i}")
            
            nodeServer.OLDVALUE = self.OLDVALUE
            nodeServer.VALUE = self.VALUE

            # Calculate time spent in this iteration
            iteration_time = time.time() - iteration_start
            print(f"{self.HOST} completed iteration {i} in {iteration_time:.2f} seconds")