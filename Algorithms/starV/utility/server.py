import socket
import threading
import _thread
import time
import pickle
from phe import paillier
import numpy as np

class Server(threading.Thread):
    def __init__(self, HOST, PORT, VALUE, ITERATION, NEIGHBORS, ALGORITHM):
        threading.Thread.__init__(self)
        self.HOST = HOST
        self.PORT = PORT
        self.VALUE = VALUE
        self.OLDVALUE = VALUE.copy() if isinstance(VALUE, np.ndarray) else VALUE
        self.NRNEIGHBORS = len(NEIGHBORS)
        self.CLOSEDNEIGHBORS = []
        self.YIJ = {}
        self.ITERATION = ITERATION
        self.ALGORITHM = ALGORITHM
        self.VALUECHANGE = False
        self.CLOSE = False
        self.CLOSED = False
        self.COMPLETED = False
        print(f"Creating Server on {HOST} with Port {PORT} and value {VALUE}")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.HOST, self.PORT))
            s.settimeout(1)  # Set a short timeout for the accept() call
            s.listen()
            print(f"{self.HOST} is listening")
            while not self.CLOSE:
                try:
                    conn, addr = s.accept()
                    print(f"{self.HOST} is connected by {addr}")
                    _thread.start_new_thread(self.handleClient, (conn,addr))
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error in server accept: {e}")
                    if self.CLOSE:
                        break
            print(f"Closing server for {self.HOST}")
            self.CLOSED = True

    def handleClient(self, conn, addr):
        try:
            with conn:
                data = conn.recv(1024)
                if not data:
                    print(f"ERROR IN TRANSMISSION - NODE: {self.HOST}")
                    return -1
                if data == b'close':
                    conn.sendall(b'bye')
                    self.NRNEIGHBORS -= 1
                    if self.NRNEIGHBORS == 0:
                        self.CLOSE = True
                elif data == b'check_completed':
                    conn.sendall(b'completed' if self.COMPLETED else b'not_completed')
                else:
                    if self.ALGORITHM == 1:    
                        data = int(data)
                        if data < self.ITERATION:
                            conn.sendall(pickle.dumps(self.OLDVALUE))
                        elif data > self.ITERATION:
                            conn.sendall(pickle.dumps(np.array([-1])))
                        else:
                            conn.sendall(pickle.dumps(self.VALUE))
                    elif self.ALGORITHM == 2:
                        if data == b'average':
                            self.handle_average(conn)
                        elif int(data) == 1:
                            self.handle_mode_1(conn)
                        elif int(data) == 2:
                            self.handle_mode_2(conn)
        except Exception as e:
            print(f"Error handling client {addr}: {e}")

    def handle_average(self, conn):
        try:
            conn.sendall(b'ack')
            data = conn.recv(1024)
            it = int(data)

            if it < self.ITERATION:
                conn.sendall(b'ok')
                data = pickle.loads(conn.recv(8192))
                public_key = paillier.PaillierPublicKey(int(data))
                conn.sendall(b'ack')
                data_val = pickle.loads(conn.recv(8192))
                conn.sendall(b'ack')
                data_exp = pickle.loads(conn.recv(8192))
                conn.sendall(b'ack')
                weight = float(pickle.loads(conn.recv(2048)))
                val = [paillier.EncryptedNumber(public_key, int(v), int(e)) for v, e in zip(data_val, data_exp)]
                val = [v + weight * ov for v, ov in zip(val, self.OLDVALUE)]
                data_val = pickle.dumps([str(v.ciphertext()) for v in val])
                data_exp = pickle.dumps([str(v.exponent) for v in val])
                conn.sendall(data_val)
                conn.recv(1024)
                conn.sendall(data_exp)
            elif it > self.ITERATION:
                conn.sendall(b'big')
            else:
                conn.sendall(b'ok')
                data = pickle.loads(conn.recv(8192))
                public_key = paillier.PaillierPublicKey(int(data))
                conn.sendall(b'ack')
                data_val = pickle.loads(conn.recv(8192))
                conn.sendall(b'ack')
                data_exp = pickle.loads(conn.recv(8192))
                conn.sendall(b'ack')
                weight = float(pickle.loads(conn.recv(2048)))
                val = [paillier.EncryptedNumber(public_key, int(v), int(e)) for v, e in zip(data_val, data_exp)]
                if it != self.ITERATION:
                    val = [v + weight * ov for v, ov in zip(val, self.OLDVALUE)]
                else:
                    val = [v + weight * cv for v, cv in zip(val, self.VALUE)]
                data_val = pickle.dumps([str(v.ciphertext()) for v in val])
                data_exp = pickle.dumps([str(v.exponent) for v in val])
                conn.sendall(data_val)
                conn.recv(1024)
                conn.sendall(data_exp)
        except Exception as e:
            print(f"Error in handle_average: {e}")

    def handle_mode_1(self, conn):
        conn.sendall(b'ok')
        data = conn.recv(1024)
        self.CLOSEDNEIGHBORS.append(pickle.loads(data))

    def handle_mode_2(self, conn):
        conn.sendall(b'ok')
        data = conn.recv(1024)
        host = data.decode()
        conn.sendall(b'ok')
        data = conn.recv(1024)
        self.YIJ[host] = float(data)